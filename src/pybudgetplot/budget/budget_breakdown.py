"""This module defines the logic for dealing with the budged daly breakdowns."""
from io import BytesIO

from pandas import DataFrame, DatetimeIndex, Series, concat, date_range
from xlsxwriter import Workbook
from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell

from pybudgetplot.budget.budget_definition import BudgetDefinition


def calculate_breakdown(budget: BudgetDefinition) -> DataFrame:
    """Calculates the breakdown of the budget's "daily" and "cumulative" totals.

    Args:
        budget: Budget definition.

    Returns:
        DataFrame with the breakdown values.
    """

    breakdown_data = DataFrame(
        index=date_range(budget.period.start, budget.period.end)
    )

    for item in budget.items:
        item_dates = budget.period.generate_dates(item.frequency)
        item_data = DataFrame(
            data={item.description: item.amount},
            index=DatetimeIndex(Series(item_dates, dtype=object))
        )
        breakdown_data = concat([breakdown_data, item_data], axis=1).fillna(0)

    breakdown_data["daily_total"] = breakdown_data.sum(axis=1)
    breakdown_data["cumulative_total"] = breakdown_data["daily_total"].cumsum()
    breakdown_data.index.rename("date", True)
    return breakdown_data


def breakdown_as_csv(breakdown: DataFrame) -> bytes:
    """Returns the breakdown data formatted as CSV bytes."""

    buffer = BytesIO()
    breakdown.to_csv(
        buffer,
        index_label="date",
        encoding="utf-8",
        errors="surrogateescape",
        line_terminator="\n",
        float_format="%.f",
        date_format="%Y-%m-%d",
    )
    return buffer.getvalue()


def breakdown_as_excel(breakdown: DataFrame, sheet_name="Breakdown") -> bytes:
    """Generates Excel document from budged breakdown DataFrame."""

    buffer = BytesIO()
    workbook = Workbook(buffer)
    worksheet = workbook.add_worksheet(sheet_name)

    column_names = ["DATE"] + breakdown.axes[1].to_list()
    column_names[-2:] = ["DAILY_TOTAL", "CUMULATIVE_TOTAL"]

    idx_cum_total = len(column_names) - 1
    idx_total = idx_cum_total - 1

    fmt_header = workbook.add_format({
        "bold": True,
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "top": 2,
        "bottom": 2,
    })

    fmt_date = workbook.add_format({
        "num_format": "yyyy-mm-dd",
        "align": "center",
        "valign": "vcenter",
        "left": 2,
        "right": 2,
    })

    fmt_item = workbook.add_format({
        "num_format": "[Blue]General;[Red]-General;General",
        "valign": "vcenter",
    })

    fmt_total = workbook.add_format({
        "italic": True,
        "num_format": "[Blue]General;[Red]-General;General",
        "valign": "vcenter",
        "left": 2,
        "right": 2,
    })

    fmt_cum_total = workbook.add_format({
        "bold": True,
        "num_format": "[Blue]General;[Red]-General;General",
        "valign": "vcenter",
        "left": 2,
        "right": 2,
    })

    rows = [
        ([item[0].date()] + [int(_) for _ in item[1:]])
        for item
        in breakdown.itertuples()
    ]

    def get_column_format(col_idx: int):
        """Deduce and return the correct format for cells in a given column."""

        if col_idx == 0:
            return fmt_date

        if col_idx == idx_cum_total:
            return fmt_cum_total

        if col_idx == idx_total:
            return fmt_total

        return fmt_item

    # add_formulas_to_rows
    for current_row_idx, current_row in enumerate(rows, start=1):
        first_item_cell = xl_rowcol_to_cell(current_row_idx, 1)
        last_item_cell = xl_rowcol_to_cell(current_row_idx, idx_total - 1)
        total_formula = f"=SUM({first_item_cell}:{last_item_cell})"
        current_row[idx_total] = total_formula  # noqa
        total_cell = xl_rowcol_to_cell(current_row_idx, idx_total)
        cum_total_formula = f"={total_cell}"
        if current_row_idx > 1:
            previous = xl_rowcol_to_cell(current_row_idx - 1, idx_cum_total)
            cum_total_formula += f"+{previous}"
        current_row[idx_cum_total] = cum_total_formula  # noqa

    # add_table_to_sheet
    table_columns = [
        {
            "header": column_name,
            "header_format": fmt_header,
            "format": get_column_format(column_name_idx),
        }
        for (column_name_idx, column_name) in enumerate(column_names)
    ]

    table_columns[0]["total_string"] = "TOTALS"
    for i in range(1, idx_total):
        table_columns[i]["total_function"] = "sum"

    table = {
        "total_row": 1,
        "header_row": 1,
        "autofilter": False,
        "style": "Table Style Light 11",
        "first_column": True,
        "last_column": True,
        "banded_columns": True,
        "banded_rows": False,
        "data": rows,
        "columns": table_columns,
    }

    worksheet.add_table(0, 0, len(rows) + 1, idx_cum_total, table)

    # add_config_to_sheet
    worksheet.freeze_panes(1, 1)
    worksheet.ignore_errors({"formula_range": "A1:XFD1048576"})

    for column_name_index, column_name in enumerate(column_names):
        col_start = xl_col_to_name(column_name_index)
        col_end = xl_col_to_name(column_name_index)
        col_addr = f"{col_start}:{col_end}"
        col_width = 10 if (column_name_index == 0) else (len(column_name) + 2)
        worksheet.set_column(col_addr, col_width)

    workbook.close()
    return buffer.getvalue()
