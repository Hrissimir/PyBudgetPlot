import logging
import re
import warnings
from dataclasses import InitVar, dataclass, field
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO, StringIO
from typing import List, Union

import yaml
from dateutil import rrule
from pandas import DataFrame, DatetimeIndex, Series, Timestamp, concat, date_range
from recurrent import RecurringEvent
from xlsxwriter import Workbook
from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

DateStamp = Union[None, int, str, date, datetime, Timestamp]


@dataclass
class DatePeriod:
    """Represents the period of dates between two Timestamps."""

    start_date: InitVar[DateStamp]
    end_date: InitVar[DateStamp]

    start: Timestamp = field(
        init=False, repr=True, hash=True, compare=True, default=None,
    )
    end: Timestamp = field(
        init=False, repr=True, hash=True, compare=True, default=None,
    )

    def __post_init__(self, start_date: DateStamp, end_date: DateStamp):
        """Post-initialize new DatePeriod instance."""

        self.start = self.parse_datestamp(start_date)
        self.end = self.parse_datestamp(end_date)

    def __str__(self) -> str:
        start_value = self.format_timestamp(self.start)
        end_value = self.format_timestamp(self.end)
        return f"['{start_value}' - '{end_value}']"

    @classmethod
    def parse_datestamp(cls, value: DateStamp) -> Timestamp:
        """Parse and return normalized Timestamp from any value."""

        if value is None:
            raise ValueError(value)

        if isinstance(value, Timestamp):
            timestamp = value
        else:
            try:
                timestamp = Timestamp(value)
            except Exception as ex:
                raise ValueError(value) from ex

        if cls.is_datestamp(timestamp):
            return timestamp

        return timestamp.normalize()

    @classmethod
    def is_datestamp(cls, stamp: Timestamp) -> bool:
        """Checks if the stamp is a 'date-stamp' (e.g. normalized)."""

        if not isinstance(stamp, Timestamp):
            raise TypeError(stamp, Timestamp, type(stamp))
        return (
                (stamp.hour == 0)
                and (stamp.minute == 0)
                and (stamp.second == 0)
                and (stamp.microsecond == 0)
        )

    @classmethod
    def format_timestamp(cls, stamp: Timestamp) -> str:
        """Formats a Timestamp to string.

        If the Timestamp is 'normalized', resulting string is in ISO-dateformat,
        otherwise the result of the default Timestamp.__str__() is returned.

        Args:
            stamp: Timestamp instance.

        Returns:
            The resulting string.
        """

        if cls.is_datestamp(stamp):
            return stamp.date().isoformat()

        return str(stamp)

    def generate_dates(self, frequency: str) -> List[Timestamp]:
        """Returns list of dates within the period, with the given frequency."""

        # check to see if the frequency can be parsed to a single date.
        try:
            result = [self.parse_datestamp(frequency)]
        except ValueError:
            result = None

        if result is None:

            # try to parse the frequency using the 'recurrent' lib
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    event = RecurringEvent()
                    event.parse(frequency)
                    rule = rrule.rrulestr(event.get_RFC_rrule())

                    # ensure all Timestamps are normalized.
                    result = [
                        Timestamp(occurrence).normalize()
                        for occurrence
                        in rule.between(self.start, self.end, inc=True)
                    ]

            except Exception as ex:

                # raise if the frequency could not be parsed
                raise ValueError(frequency) from ex

        return result


@dataclass
class BudgetItem:
    """Represents the definition of a single, recurring item from the budget."""

    item_desc: InitVar[Union[str, None]]
    item_amount: InitVar[Union[int, float, str, None]]
    item_freq: InitVar[Union[str, None]]

    description: str = field(
        init=False, repr=True, hash=True, compare=True
    )
    amount: int = field(
        init=False, repr=True, hash=True, compare=True
    )
    frequency: str = field(
        init=False, repr=True, hash=True, compare=True
    )

    def __post_init__(
            self,
            item_desc: Union[str, None],
            item_amount: Union[int, float, str, None],
            item_freq: Union[str, None]
    ):
        """Post-initialize a new BudgetItem instance."""

        self.description = self.normalize_string(item_desc)
        self.amount = self.parse_int(item_amount)
        self.frequency = self.normalize_string(item_freq)

    @classmethod
    def normalize_string(cls, value: str) -> str:
        """Normalizes the whitespaces in the value then strips and return it."""

        result = re.sub(r"\s+", " ", value).strip()
        if not result:
            raise ValueError(value)
        return result

    @classmethod
    def parse_int(cls, value) -> int:
        """Parses the value to int and returns the result."""

        if isinstance(value, int):
            return value
        try:
            str_value = cls.normalize_string(str(value))
            decimal_value = Decimal(str_value).to_integral_value(ROUND_HALF_UP)
            return int(decimal_value)
        except Exception as ex:
            raise ValueError(value) from ex


@dataclass
class BudgetDefinition:
    """The budget-definition consists of a period and a list of budget items."""

    period_start: InitVar[DateStamp]
    period_end: InitVar[DateStamp]

    period: DatePeriod = field(
        init=False, repr=True, hash=True, compare=True, default=False,
    )

    items: List[BudgetItem] = field(
        init=True, repr=True, hash=True, compare=True, default_factory=list,
    )

    def __post_init__(self, period_start: DateStamp, period_end: DateStamp):
        """Post-initialize new BudgetDefinition instance."""

        self.period = DatePeriod(period_start, period_end)

    @classmethod
    def from_dict(cls, data: dict) -> "BudgetDefinition":
        """Creates new Budget instance from data dict."""

        period_data = data["PERIOD"]
        period_start = period_data["start"]
        period_end = period_data["end"]

        budget = BudgetDefinition(period_start, period_end)

        items_data = data["ITEMS"]
        for item_desc, item_data in items_data.items():
            item_amount = item_data["amount"]
            item_frequency = item_data["frequency"]
            budget.add_item(item_desc, item_amount, item_frequency)

        return budget

    @classmethod
    def from_yaml(cls, text) -> "BudgetDefinition":
        """Parses and returns Budget instance from YAML text."""

        buffer = StringIO(text)
        data = yaml.load(buffer, Loader=yaml.SafeLoader)
        return cls.from_dict(data)

    def add_item(self, description, amount, frequency):
        """Creates and adds new Item to the list of items."""

        item = BudgetItem(description, amount, frequency)
        self.items.append(item)

    def as_dict(self) -> dict:
        """Returns a dict with the budget definition data."""

        return {
            "PERIOD": {
                "start": self.period.start.date().isoformat(),
                "end": self.period.end.date().isoformat()
            },
            "ITEMS": {
                item.description: {
                    "amount": item.amount,
                    "frequency": item.frequency
                }
                for item
                in self.items
            },
        }

    def as_yaml(self) -> str:
        """Formats the budged definition in YAML format."""

        data = self.as_dict()
        buffer = StringIO(newline="\n")
        yaml.dump(
            data,
            buffer,
            Dumper=yaml.SafeDumper,
            indent=4,
            width=80,
            allow_unicode=True,
            line_break="\n",
            encoding="utf-8",
            sort_keys=False,
        )
        return buffer.getvalue()

    def calculate_breakdown(self) -> DataFrame:
        """Calculates a breakdown of the "daily" and "cumulative" totals."""

        df = DataFrame(
            index=date_range(self.period.start, self.period.end)
        )

        for item in self.items:
            item_dates = self.period.generate_dates(item.frequency)
            item_df = DataFrame(
                data={item.description: item.amount},
                index=DatetimeIndex(Series(item_dates, dtype=object))
            )
            df = concat([df, item_df], axis=1).fillna(0)

        df["daily_total"] = df.sum(axis=1)
        df["cumulative_total"] = df["daily_total"].cumsum()
        df.index.rename("date", True)
        return df

    def to_csv(self) -> bytes:
        """Returns the breakdown of the current budget as CSV bytes."""

        buffer = BytesIO()
        breakdown = self.calculate_breakdown()
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

    def to_xlsx(self, sheet_name="Breakdown") -> bytes:
        """Generates Excel document from budged breakdown DataFrame."""

        breakdown = self.calculate_breakdown()
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


@dataclass
class BudgetBreakdown:
    """Break-down of BudgetDefinition 'daily' and 'cumulative' total values."""

    budget: InitVar[BudgetDefinition]

    data_frame: DataFrame = field(
        init=False, repr=True, hash=True, compare=True, default=None
    )

    def __post_init__(self, budget: BudgetDefinition):
        """Post-initialize a new BudgetBreakdown instance."""

        if not isinstance(budget, BudgetDefinition):
            raise TypeError(budget, BudgetDefinition, type(budget))

        period = budget.period
        if not isinstance(period, DatePeriod):
            raise TypeError(period, DatePeriod, type(period))

        items = budget.items
        if not isinstance(items, list):
            raise TypeError(items, list, type(items))

        df = DataFrame(
            index=date_range(
                start=period.start,
                end=period.end,
            )
        )

        for item in items:
            item_dates = period.generate_dates(item.frequency)
            item_df = DataFrame(
                data={item.description: item.amount},
                index=DatetimeIndex(Series(item_dates, dtype=object))
            )
            df = concat([df, item_df], axis=1).fillna(0)

        df["daily_total"] = df.sum(axis=1)
        df["cumulative_total"] = df["daily_total"].cumsum()
        df.index.rename("date", True)
        self.data_frame = df
