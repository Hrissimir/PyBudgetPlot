"""Helper module for creating XLSX file with the budget breakdown data."""
import logging
from io import BytesIO

from pandas import DataFrame
from xlsxwriter import Workbook
from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

FMT_HEADER = {
    "bold": True,
    "align": "center",
    "valign": "vcenter",
    "border": 1,
    "top": 2,
    "bottom": 2,
}

FMT_DATE = {
    "num_format": "yyyy-mm-dd",
    "align": "center",
    "valign": "vcenter",
    "left": 2,
    "right": 2,
}

FMT_AMOUNT = {
    "num_format": "[Blue]General;[Red]-General;General",
    "valign": "vcenter",
}

FMT_DAILY = {
    "italic": True,
    "num_format": "[Blue]General;[Red]-General;General",
    "valign": "vcenter",
    "left": 2,
    "right": 2,
}

FMT_CUMULATIVE = {
    "bold": True,
    "num_format": "[Blue]General;[Red]-General;General",
    "valign": "vcenter",
    "left": 2,
    "right": 2,
}


def generate_xlsx(data: DataFrame, sheet_name="Breakdown") -> bytes:
    """Generates Excel document from DataFrame containing budged breakdown."""

    # prepare worksheet
    buffer = BytesIO()
    workbook = Workbook(buffer)
    worksheet = workbook.add_worksheet(sheet_name)

    # init formats
    fmt_header = workbook.add_format(FMT_HEADER)
    fmt_date = workbook.add_format(FMT_DATE)
    fmt_amount = workbook.add_format(FMT_AMOUNT)
    fmt_daily = workbook.add_format(FMT_DAILY)
    fmt_cumulative = workbook.add_format(FMT_CUMULATIVE)

    # extract the column names
    column_names = ["DATE"] + data.axes[1].to_list()
    column_names[-2:] = ["DAILY", "CUMULATIVE"]

    # calculate the indexes of the 'daily' and 'cumulative' columns
    idx_cumulative = len(column_names) - 1
    idx_daily = idx_cumulative - 1

    def get_cell_format(column_index_: int):
        """Get format for a cell that belongs to column with the given index."""

        if column_index_ == 0:
            return fmt_date

        if column_index_ == idx_cumulative:
            return fmt_cumulative

        if column_index_ == idx_daily:
            return fmt_daily

        return fmt_amount

    # extract the rows data
    rows_data = [
        ([item[0].date()] + [float(_) for _ in item[1:]])
        for item
        in data.itertuples()
    ]

    # replace the values of all 'daily' and 'cumulative' cells with formulas
    for row_index, row_cells in enumerate(rows_data, start=1):
        first_amount_cell = xl_rowcol_to_cell(row_index, 1)
        last_amount_cell = xl_rowcol_to_cell(row_index, idx_daily - 1)
        daily_formula = f"=SUM({first_amount_cell}:{last_amount_cell})"
        row_cells[idx_daily] = daily_formula  # noqa
        daily_cell = xl_rowcol_to_cell(row_index, idx_daily)
        cumulative_formula = f"={daily_cell}"
        if row_index > 1:
            previous_row_cumulative_cell = xl_rowcol_to_cell(
                row_index - 1,
                idx_cumulative
            )
            cumulative_formula += f"+{previous_row_cumulative_cell}"
        row_cells[idx_cumulative] = cumulative_formula  # noqa

    # prepare columns for Excel table
    excel_table_columns = [
        {
            "header": col_name,
            "header_format": fmt_header,
            "format": get_cell_format(col_idx)
        }
        for (col_idx, col_name)
        in enumerate(column_names)
    ]

    # add a 'totals' row at the bottom of the Excel table
    excel_table_columns[0]["total_string"] = "TOTALS"
    for i in range(1, idx_daily):
        excel_table_columns[i]["total_function"] = "sum"

    # create the Excel table
    excel_table = {
        "total_row": 1,
        "header_row": 1,
        "autofilter": False,
        "style": "Table Style Light 11",
        "first_column": True,
        "last_column": True,
        "banded_columns": True,
        "banded_rows": False,
        "data": rows_data,
        "columns": excel_table_columns,
    }

    # add the Excel table to the sheet
    worksheet.add_table(0, 0, len(rows_data) + 1, idx_cumulative, excel_table)

    # freeze the first row and the first column
    worksheet.freeze_panes(1, 1)

    # ignore format warnings
    worksheet.ignore_errors({"formula_range": "A1:XFD1048576"})

    # adjust the columns width
    for column_index, column_name in enumerate(column_names):
        column_xl_name = xl_col_to_name(column_index)
        column_xl_address = f"{column_xl_name}:{column_xl_name}"
        column_width = 10 if (column_index == 0) else (len(column_name) + 2)
        worksheet.set_column(column_xl_address, column_width)

    workbook.close()
    return buffer.getvalue()
