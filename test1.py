from __future__ import annotations

from pathlib import Path
from typing import Mapping, Optional, TypedDict

import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string


class ColumnSpec(TypedDict, total=False):
    """Mapping spec for a single dataframe column."""
    sheet_name: str
    start_cell: str
    clear_rows: Optional[int]


def _parse_cell(cell: str) -> tuple[int, int]:
    """Return (row_index, col_index) 1-based for an A1-style address."""
    col_letters, row = coordinate_from_string(cell)
    return int(row), int(column_index_from_string(col_letters))


def _clear_column_block(ws, start_cell: str, n_rows: int) -> None:
    start_row, start_col = _parse_cell(start_cell)
    for r in range(start_row, start_row + n_rows):
        ws.cell(row=r, column=start_col, value=None)


def _write_column_values(ws, start_cell: str, values: list[object]) -> None:
    start_row, start_col = _parse_cell(start_cell)
    for i, v in enumerate(values):
        ws.cell(row=start_row + i, column=start_col, value=v)


def populate_excel_template_by_columns(
    *,
    template_path: str | Path,
    output_path: str | Path,
    df: pd.DataFrame,
    mapping: Mapping[str, ColumnSpec],
) -> Path:
    """Copy an immutable Excel template and populate cells from DataFrame columns.

    Each key in `mapping` must be a column name in `df`.
    Each value provides where that column should be written (sheet + start cell).
    Template structure is not altered (no inserts, no table resizing).

    Args:
        template_path: Path to the .xlsx template file.
        output_path: Path where the populated workbook will be saved.
        df: DataFrame containing the source data.
        mapping: Dict keyed by DataFrame column name. Example:
            {
              "Data Entity": {"sheet_name": "Sheet1", "start_cell": "B15", "clear_rows": 200},
              "Description": {"sheet_name": "Sheet1", "start_cell": "C15", "clear_rows": 200},
            }

    Returns:
        Path to the saved workbook.
    """
    template_path = Path(template_path)
    output_path = Path(output_path)

    if not template_path.exists():
        raise FileNotFoundError(template_path)
    if df.empty:
        raise ValueError("DataFrame is empty, nothing to write.")

    # Validate mapping columns exist
    missing_cols = [col for col in mapping.keys() if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing DataFrame columns required by mapping: {missing_cols}")

    wb = load_workbook(template_path)

    for df_col, spec in mapping.items():
        sheet_name = spec["sheet_name"]
        start_cell = spec["start_cell"]
        clear_rows = spec.get("clear_rows")

        if sheet_name not in wb.sheetnames:
            raise KeyError(f"Worksheet '{sheet_name}' not found. Available: {wb.sheetnames}")

        ws = wb[sheet_name]
        values = df[df_col].tolist()

        if clear_rows is not None:
            _clear_column_block(ws, start_cell, n_rows=int(clear_rows))

        _write_column_values(ws, start_cell, values)

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
        "Data Entity": {"sheet_name": "Sheet1", "start_cell": "B15", "clear_rows": 200},
        "Description": {"sheet_name": "Sheet1", "start_cell": "C15", "clear_rows": 200},
    }

    populate_excel_template_by_columns(
        template_path="template.xlsx",
        output_path="output/my_report.xlsx",
        df=df,
        mapping=mapping,
    )