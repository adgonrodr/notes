from __future__ import annotations

from pathlib import Path
from typing import Mapping, Optional, TypedDict

import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string


class ColumnSpec(TypedDict, total=False):
    sheet_name: str
    start_cell: str
    clear_rows: Optional[int]


def _parse_cell(cell: str) -> tuple[int, int]:
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


def _populate_by_columns(
    wb,
    *,
    df: pd.DataFrame,
    mapping: Mapping[str, ColumnSpec],
) -> None:
    if df.empty:
        raise ValueError("One of the provided DataFrames is empty, nothing to write.")

    missing_cols = [col for col in mapping.keys() if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing DataFrame columns required by mapping: {missing_cols}")

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


def populate_excel_template_two_tables(
    *,
    template_path: str | Path,
    output_path: str | Path,
    main_df: pd.DataFrame,
    main_mapping: Mapping[str, ColumnSpec],
    side_df: pd.DataFrame,
    side_mapping: Mapping[str, ColumnSpec],
) -> Path:
    """Populate two independent table areas in an immutable Excel template."""
    template_path = Path(template_path)
    output_path = Path(output_path)

    if not template_path.exists():
        raise FileNotFoundError(template_path)

    wb = load_workbook(template_path)

    _populate_by_columns(wb, df=main_df, mapping=main_mapping)
    _populate_by_columns(wb, df=side_df, mapping=side_mapping)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path


# Example usage
if __name__ == "__main__":
    main_df = pd.DataFrame(
        {
            "Data Entity": ["Customer", "Order"],
            "Description": ["CRM record", "Sales order"],
        }
    )

    side_df = pd.DataFrame(
        {
            "Metric": ["Total Entities", "Total Fields"],
            "Value": [2, 15],
        }
    )

    main_mapping = {
        "Data Entity": {"sheet_name": "Sheet1", "start_cell": "B15", "clear_rows": 200},
        "Description": {"sheet_name": "Sheet1", "start_cell": "C15", "clear_rows": 200},
    }

    side_mapping = {
        "Metric": {"sheet_name": "Sheet1", "start_cell": "H15", "clear_rows": 50},
        "Value": {"sheet_name": "Sheet1", "start_cell": "I15", "clear_rows": 50},
    }

    populate_excel_template_two_tables(
        template_path="template.xlsx",
        output_path="output/my_report.xlsx",
        main_df=main_df,
        main_mapping=main_mapping,
        side_df=side_df,
        side_mapping=side_mapping,
    )