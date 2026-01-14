from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string


@dataclass(frozen=True)
class CellBlockTarget:
    """Target block in a template to populate with a dataframe.

    Attributes:
        sheet_name: Worksheet name.
        start_cell: Top-left cell where the dataframe body starts, e.g. "B15".
        clear_rows: If set, clears this many rows x dataframe columns before writing.
            Use this when you need to guarantee no leftover data from prior runs.
    """
    sheet_name: str
    start_cell: str
    clear_rows: Optional[int] = None


def _parse_cell(cell: str) -> tuple[int, int]:
    """Return (row_index, col_index) 1-based for an A1-style address."""
    col_letters, row = coordinate_from_string(cell)
    return int(row), int(column_index_from_string(col_letters))


def _clear_block(ws, start_cell: str, n_rows: int, n_cols: int) -> None:
    start_row, start_col = _parse_cell(start_cell)
    for r in range(start_row, start_row + n_rows):
        for c in range(start_col, start_col + n_cols):
            ws.cell(row=r, column=c, value=None)


def _write_df_values(
    ws,
    df: pd.DataFrame,
    start_cell: str,
    *,
    include_headers: bool = False,
) -> None:
    start_row, start_col = _parse_cell(start_cell)

    if include_headers:
        for j, col_name in enumerate(df.columns, start=0):
            ws.cell(row=start_row, column=start_col + j, value=str(col_name))
        start_row += 1

    # Faster than iterrows for most cases
    values = df.to_numpy()
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            ws.cell(row=start_row + i, column=start_col + j, value=values[i, j])


def populate_excel_template_cells(
    *,
    template_path: str | Path,
    output_path: str | Path,
    df: pd.DataFrame,
    mapping: Mapping[str, CellBlockTarget],
    key: str,
    include_headers: bool = False,
) -> Path:
    """Copy an immutable Excel template and populate a mapped cell block.

    Args:
        template_path: Path to the .xlsx template file.
        output_path: Path where the populated workbook will be saved.
        df: DataFrame with the data to write.
        mapping: Dict mapping a logical name to a CellBlockTarget.
        key: Which mapping entry to use.
        include_headers: Writes dataframe column names at the start_cell row.

    Returns:
        Path to the saved workbook.
    """
    template_path = Path(template_path)
    output_path = Path(output_path)

    if not template_path.exists():
        raise FileNotFoundError(template_path)
    if df.empty:
        raise ValueError("DataFrame is empty, nothing to write.")
    if key not in mapping:
        raise KeyError(f"Unknown mapping key '{key}'. Available: {list(mapping.keys())}")

    target = mapping[key]

    wb = load_workbook(template_path)
    if target.sheet_name not in wb.sheetnames:
        raise KeyError(
            f"Worksheet '{target.sheet_name}' not found. Available: {wb.sheetnames}"
        )
    ws = wb[target.sheet_name]

    # Optional: clear a fixed number of rows to prevent stale data
    if target.clear_rows:
        header_offset = 1 if include_headers else 0
        _clear_block(
            ws,
            target.start_cell,
            n_rows=target.clear_rows + header_offset,
            n_cols=len(df.columns),
        )

    _write_df_values(ws, df, target.start_cell, include_headers=include_headers)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path


# Example
if __name__ == "__main__":
    df = pd.DataFrame(
        {
            "Data Entity": ["Customer", "Order"],
            "Description": ["CRM record", "Sales order"],
        }
    )

    mapping = {
        "entities_block": CellBlockTarget(
            sheet_name="Sheet1",
            start_cell="B15",
            clear_rows=200,  # set to None if you do not want to clear anything
        )
    }

    populate_excel_template_cells(
        template_path="template.xlsx",
        output_path="output/my_report.xlsx",
        df=df,
        mapping=mapping,
        key="entities_block",
        include_headers=False,
    )