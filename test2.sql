CREATE OR REPLACE PROCEDURE PARSE_EXCEL_TABLES(
    STAGE_PATH STRING,          -- Example: '@MY_STAGE/reports/file.xlsx'
    SHEET_NAME STRING,          -- Example: 'Sheet1'
    SPECS VARIANT,              -- JSON array of table specs (see example call)
    HEADER_SEP STRING           -- Example: ' | '
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'openpyxl', 'pandas')
HANDLER = 'run'
AS
$$
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from io import BytesIO
from typing import Dict, List, Optional, Sequence, Tuple, Any

import pandas as pd
from openpyxl import load_workbook
from snowflake.snowpark import Session
from snowflake.snowpark.files import SnowflakeFile


def normalise_merged_cells(ws) -> None:
    """Normalise merged cells by copying the anchor value across the merged range.

    Args:
        ws: An openpyxl worksheet.

    Returns:
        None. The worksheet is modified in-place.
    """
    for merged_range in list(ws.merged_cells.ranges):
        value = ws.cell(merged_range.min_row, merged_range.min_col).value
        if value is None:
            continue
        for r in range(merged_range.min_row, merged_range.max_row + 1):
            for c in range(merged_range.min_col, merged_range.max_col + 1):
                ws.cell(r, c).value = value


def sheet_to_grid(ws) -> List[List[object]]:
    """Convert a worksheet to a 2D grid of cell values.

    Whitespace-only strings are normalised to None.

    Args:
        ws: An openpyxl worksheet.

    Returns:
        A list of rows, where each row is a list of cell values.
    """
    grid: List[List[object]] = []
    for r in range(1, ws.max_row + 1):
        row: List[object] = []
        for c in range(1, ws.max_column + 1):
            v = ws.cell(r, c).value
            if isinstance(v, str) and not v.strip():
                v = None
            row.append(v)
        grid.append(row)
    return grid


def _ffill(values: List[object]) -> List[object]:
    """Forward-fill None values within a single list.

    Args:
        values: A list of values which may include None entries.

    Returns:
        A new list where None entries are replaced with the most recent non-None value.
    """
    out: List[object] = []
    last: Optional[object] = None
    for v in values:
        if v is None:
            out.append(last)
        else:
            last = v
            out.append(v)
    return out


def build_flat_columns(
    header_rows: Sequence[Sequence[object]],
    sep: str = " | ",
    drop_repeated: bool = True,
) -> List[str]:
    """Flatten 1..N header rows into a single list of column names.

    Approach:
      - Forward-fill blanks in each header row (useful for grouped headers from merged cells).
      - Join non-empty parts per column using a separator.
      - Ensure uniqueness (duplicate names get a suffix like " (2)").

    Args:
        header_rows: A sequence of header rows. Each header row is a sequence of cell values.
        sep: Separator used to join header parts.
        drop_repeated: If True, consecutive identical parts are collapsed.

    Returns:
        A list of flattened, unique column names.
    """
    if not header_rows:
        return []

    width = max(len(r) for r in header_rows)
    norm = [list(r) + [None] * (width - len(r)) for r in header_rows]
    norm = [_ffill(r) for r in norm]

    cols: List[str] = []
    for j in range(width):
        parts: List[str] = []
        prev: Optional[str] = None
        for i in range(len(norm)):
            v = norm[i][j]
            if v is None:
                continue
            s = str(v).strip()
            if not s:
                continue
            if drop_repeated and prev == s:
                continue
            parts.append(s)
            prev = s
        cols.append(sep.join(parts) if parts else f"col_{j}")

    seen: Dict[str, int] = {}
    unique_cols: List[str] = []
    for c in cols:
        n = seen.get(c, 0)
        unique_cols.append(c if n == 0 else f"{c} ({n + 1})")
        seen[c] = n + 1

    return unique_cols


def last_data_row_in_span(
    grid: List[List[object]],
    start_row: int,
    col_span: Tuple[int, int],
    max_blank_streak: int = 1,
) -> int:
    """Infer the last row of a table block based on data presence.

    Scans downward starting at start_row, looking for any non-empty cell
    in the given column span. Once max_blank_streak consecutive blank rows
    are seen, scanning stops and the most recent row containing data is returned.

    Args:
        grid: 2D grid of worksheet values.
        start_row: 1-based row index to start scanning.
        col_span: A (left_col, right_col) 1-based inclusive column span.
        max_blank_streak: Number of consecutive blank rows that ends the scan.

    Returns:
        The 1-based index of the last row that contained data in the column span.
    """
    left_col, right_col = col_span
    blank_streak = 0
    last_seen = start_row

    for r in range(start_row, len(grid) + 1):
        span = grid[r - 1][left_col - 1 : right_col]
        has_data = any(v is not None for v in span)

        if has_data:
            last_seen = r
            blank_streak = 0
        else:
            blank_streak += 1
            if blank_streak >= max_blank_streak:
                break

    return last_seen


def slice_block_to_df(
    grid: List[List[object]],
    top: int,
    left: int,
    bottom: int,
    right: int,
    header_rows: int = 1,
    header_sep: str = " | ",
) -> pd.DataFrame:
    """Slice a rectangular block and convert it into a DataFrame.

    Supports 0..N header rows:
      - 0: auto-generate column names col_0..col_n
      - 1..N: flatten header rows using build_flat_columns()

    Args:
        grid: 2D grid of worksheet values.
        top: 1-based top row index (inclusive).
        left: 1-based left column index (inclusive).
        bottom: 1-based bottom row index (inclusive).
        right: 1-based right column index (inclusive).
        header_rows: Number of header rows at the top of the block.
        header_sep: Separator used when joining multi-row header parts.

    Returns:
        A pandas DataFrame containing the sliced table.
    """
    if top < 1 or left < 1 or bottom < top or right < left:
        return pd.DataFrame()

    block = [row[left - 1 : right] for row in grid[top - 1 : bottom]]
    if not block:
        return pd.DataFrame()

    header_rows = max(0, min(int(header_rows), len(block)))
    header_part = block[:header_rows]
    body = block[header_rows:]

    if header_rows == 0:
        cols = [f"col_{i}" for i in range(len(block[0]))]
    else:
        cols = build_flat_columns(header_part, sep=header_sep)

    df = pd.DataFrame(body, columns=cols)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    return df


def extract_date_from_row(
    grid: List[List[object]],
    row: int,
    *,
    formats: Sequence[str] = ("%d-%b-%y",),
    strict: bool = False,
) -> Optional[str]:
    """Extract the first date found in a given grid row.

    Handles:
      - Excel date/datetime cell values
      - Exact strings matching formats (example: "22-Jan-26")
      - Substrings inside longer text (when strict is False)

    Args:
        grid: 2D grid of worksheet values.
        row: 1-based row index to search.
        formats: Accepted date formats (datetime.strptime). First format is output format.
        strict: If True, only accept full-cell matches. If False, also search substrings.

    Returns:
        A date formatted with formats[0], or None if no date is found.
    """
    if row < 1 or row > len(grid):
        return None

    target_fmt = formats[0]
    cells = grid[row - 1]

    def normalise(s: str) -> str:
        return s.replace("\u00a0", " ").strip()

    for v in cells:
        if isinstance(v, (dt.date, dt.datetime)):
            d = v.date() if isinstance(v, dt.datetime) else v
            return d.strftime(target_fmt)

    for v in cells:
        if isinstance(v, str):
            s = normalise(v)
            for fmt in formats:
                try:
                    parsed = dt.datetime.strptime(s, fmt).date()
                    return parsed.strftime(target_fmt)
                except ValueError:
                    continue

    if strict:
        return None

    token_re = re.compile(r"\b(\d{1,2}-[A-Za-z]{3}-\d{2,4})\b")
    for v in cells:
        if not isinstance(v, str):
            continue
        s = normalise(v)
        m = token_re.search(s)
        if not m:
            continue
        token = m.group(1)
        parts = token.split("-")
        if len(parts) == 3:
            token = f"{parts[0]}-{parts[1].title()}-{parts[2]}"

        for fmt in formats:
            try:
                parsed = dt.datetime.strptime(token, fmt).date()
                return parsed.strftime(target_fmt)
            except ValueError:
                continue

    return None


@dataclass(frozen=True)
class TableSpec:
    """Specification for extracting a table from a worksheet grid.

    Attributes:
        name: Identifier for the extracted table.
        start_row: 1-based row index where the table block starts (header begins here).
        left_col: 1-based left column index (inclusive).
        right_col: 1-based right column index (inclusive).
        header_rows: Number of header rows (0..N) to interpret.
        end_row: If provided, use as the table end row. If None, infer the end.
        max_blank_streak: Used when end_row is None. Ends the scan after N blank rows.
    """
    name: str
    start_row: int
    left_col: int
    right_col: int
    header_rows: int = 1
    end_row: Optional[int] = None
    max_blank_streak: int = 1


def _parse_specs(specs_variant: Any) -> List[TableSpec]:
    """Convert a Snowflake VARIANT into a list of TableSpec.

    Args:
        specs_variant: VARIANT expected to be an array of objects.

    Returns:
        List of TableSpec instances.

    Raises:
        ValueError: If required fields are missing.
    """
    if specs_variant is None:
        return []

    out: List[TableSpec] = []
    for item in specs_variant:
        name = item.get("name")
        start_row = item.get("start_row")
        left_col = item.get("left_col")
        right_col = item.get("right_col")
        if name is None or start_row is None or left_col is None or right_col is None:
            raise ValueError("Each spec must include name, start_row, left_col, right_col")

        out.append(
            TableSpec(
                name=str(name),
                start_row=int(start_row),
                left_col=int(left_col),
                right_col=int(right_col),
                header_rows=int(item.get("header_rows", 1)),
                end_row=(int(item["end_row"]) if item.get("end_row") is not None else None),
                max_blank_streak=int(item.get("max_blank_streak", 1)),
            )
        )
    return out


def _build_scoped_url(session: Session, stage_path: str) -> str:
    """Build a scoped URL for a staged file path.

    Args:
        session: Snowpark session.
        stage_path: File path in stage notation, example '@MY_STAGE/path/file.xlsx'.

    Returns:
        Scoped URL string to be used with SnowflakeFile.open().
    """
    # BUILD_SCOPED_FILE_URL expects a stage file path string.
    row = session.sql("SELECT BUILD_SCOPED_FILE_URL(?) AS U", params=[stage_path]).collect()[0]
    return row["U"]


def run(session: Session, stage_path: str, sheet_name: str, specs, header_sep: str):
    """Snowflake stored procedure entrypoint.

    Args:
        session: Snowpark session.
        stage_path: Staged file path, example '@MY_STAGE/reports/file.xlsx'.
        sheet_name: Worksheet name.
        specs: VARIANT array of table specs.
        header_sep: Separator used when joining multi-row header parts.

    Returns:
        VARIANT object containing extracted tables.
    """
    scoped_url = _build_scoped_url(session, stage_path)

    with SnowflakeFile.open(scoped_url, mode="rb") as f:
        content = f.read()

    wb = load_workbook(filename=BytesIO(content), data_only=True)
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Sheet '{sheet_name}' not found. Available: {wb.sheetnames}")

    ws = wb[sheet_name]
    normalise_merged_cells(ws)
    grid = sheet_to_grid(ws)

    table_specs = _parse_specs(specs)
    result: Dict[str, Any] = {}

    for spec in table_specs:
        end = spec.end_row
        if end is None:
            end = last_data_row_in_span(
                grid=grid,
                start_row=spec.start_row,
                col_span=(spec.left_col, spec.right_col),
                max_blank_streak=spec.max_blank_streak,
            )

        df = slice_block_to_df(
            grid=grid,
            top=spec.start_row,
            left=spec.left_col,
            bottom=end,
            right=spec.right_col,
            header_rows=spec.header_rows,
            header_sep=header_sep or " | ",
        )

        # Convert to JSON-friendly rows (VARIANT)
        rows = df.where(pd.notna(df), None).to_dict(orient="records")
        result[spec.name] = {
            "start_row": spec.start_row,
            "end_row": end,
            "header_rows": spec.header_rows,
            "row_count": len(rows),
            "rows": rows,
        }

    return result
$$;


CALL PARSE_EXCEL_TABLES(
  '@MY_STAGE/reports/file.xlsx',
  'Sheet1',
  PARSE_JSON('[
    {"name":"summary","start_row":2,"left_col":1,"right_col":8,"header_rows":3,"end_row":25},
    {"name":"transactions","start_row":30,"left_col":1,"right_col":12,"header_rows":1,"max_blank_streak":2}
  ]'),
  ' | '
);