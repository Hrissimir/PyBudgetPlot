"""This module defines the data and logic for calculating a budget breakdown."""

import logging
from io import BytesIO
from typing import List

import pandas
from pandas import DataFrame, DatetimeIndex, Series, concat, date_range
from xlsxwriter import Workbook
from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell

from pybudgetplot.definitions.budget import Budget

pandas.set_option("display.date_yearfirst", True)
pandas.set_option("display.float_format", lambda f: ("%.2f" % f))
pandas.set_option("display.max_columns", None)
pandas.set_option("display.max_rows", 200)
pandas.set_option("display.min_rows", 20)
pandas.set_option("display.precision", 2)
pandas.set_option("display.show_dimensions", True)
pandas.set_option("display.width", 1920)
pandas.set_option("expand_frame_repr", False)
pandas.set_option("max_colwidth", 20)
pandas.set_option("io.excel.xlsx.writer", "xlsxwriter")

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def calculate_breakdown_data(budget: Budget) -> DataFrame:
    """Calculates and returns the budget's daily breakdown data as DataFrame."""

    if not isinstance(budget, Budget):
        raise TypeError(budget, Budget, type(budget))

    data = DataFrame(
        index=date_range(
            start=budget.period.start.normalize(),
            end=budget.period.end.normalize(),
        )
    )

    for event in budget.events:
        event_dates = budget.period.generate_datestamps(event.frequency)
        event_data = DataFrame(
            data={
                event.description: event.amount,
            },
            index=DatetimeIndex(
                Series(event_dates, dtype=object)
            )
        )
        data = concat([data, event_data], axis=1).fillna(0.00)

    data["daily_total"] = data.sum(axis=1)
    data["cumulative_total"] = data["daily_total"].cumsum()
    data.index.rename("date", inplace=True)
    return data


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
FMT_EVENT = {
    "num_format": "[Blue]General;[Red]-General;General",
    "valign": "vcenter",
}

FMT_TOTAL = {
    "italic": True,
    "num_format": "[Blue]General;[Red]-General;General",
    "valign": "vcenter",
    "left": 2,
    "right": 2,
}

FMT_CUM_TOTAL = {
    "bold": True,
    "num_format": "[Blue]General;[Red]-General;General",
    "valign": "vcenter",
    "left": 2,
    "right": 2,
}


class Breakdown:
    """Represents the breakdown data of budget's daily and cumulative totals."""

    def __init__(self, budget: Budget):
        self._data = calculate_breakdown_data(budget)

    @property
    def column_names(self) -> List[str]:
        """Returns list with the column names."""

        column_names = ["DATE"] + self._data.axes[1].to_list()
        column_names[-2:] = ["DAILY_TOTAL", "CUMULATIVE_TOTAL"]
        return column_names

    @property
    def rows_data(self) -> List[list]:
        """Returns list with the row data."""

        return [
            ([item[0].date()] + [float(_) for _ in item[1:]])
            for item
            in self._data.itertuples()
        ]

    def to_csv(self) -> bytes:
        """Returns with the daily breakdown data in CSV bytes."""

        buffer = BytesIO()
        self._data.to_csv(
            buffer,
            float_format="%.2f",
            index=True,
            index_label="date",
            mode="b",
            encoding="utf-8",
            errors="surrogateescape",
            line_terminator="\n",
            date_format="%Y-%m-%d",
        )
        return buffer.getvalue()

    def to_xlsx(self, sheet_name="Breakdown") -> bytes:
        """Generates Excel document from budged breakdown DataFrame."""

        buffer = BytesIO()
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet(sheet_name)

        fmt_header = workbook.add_format(FMT_HEADER)
        fmt_date = workbook.add_format(FMT_DATE)
        fmt_event = workbook.add_format(FMT_EVENT)
        fmt_total = workbook.add_format(FMT_TOTAL)
        fmt_cum_total = workbook.add_format(FMT_CUM_TOTAL)

        column_names = self.column_names
        idx_cum_total = len(column_names) - 1
        idx_total = idx_cum_total - 1

        def get_column_format(col_idx: int):
            """Deduce and return the format for cells in a given column."""

            if col_idx == 0:
                return fmt_date

            if col_idx == idx_cum_total:
                return fmt_cum_total

            if col_idx == idx_total:
                return fmt_total

            return fmt_event

        rows_data = self.rows_data

        # add_formulas_to_rows
        for current_row_idx, current_row in enumerate(rows_data, start=1):
            first_event_cell = xl_rowcol_to_cell(current_row_idx, 1)
            last_event_cell = xl_rowcol_to_cell(current_row_idx, idx_total - 1)
            total_formula = f"=SUM({first_event_cell}:{last_event_cell})"
            current_row[idx_total] = total_formula  # noqa
            daily_total_cell = xl_rowcol_to_cell(current_row_idx, idx_total)
            cumulative_total_formula = f"={daily_total_cell}"
            if current_row_idx > 1:
                previous = xl_rowcol_to_cell(current_row_idx - 1, idx_cum_total)
                cumulative_total_formula += f"+{previous}"
            current_row[idx_cum_total] = cumulative_total_formula  # noqa

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
            "data": rows_data,
            "columns": table_columns,
        }

        worksheet.add_table(0, 0, len(rows_data) + 1, idx_cum_total, table)

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
