"""This module defines the data and logic for processing a budget definition."""

from io import BytesIO, StringIO
from typing import Dict, List, Union

import yaml
from pandas import DataFrame, DatetimeIndex, Series, concat, date_range, set_option

from pybudgetplot.definitions.event import Event
from pybudgetplot.definitions.period import Period

set_option("display.date_yearfirst", True)
set_option("display.float_format", lambda f: ("%.2f" % f))
set_option("display.max_columns", None)
set_option("display.max_rows", 200)
set_option("display.min_rows", 20)
set_option("display.precision", 2)
set_option("display.show_dimensions", True)
set_option("display.width", 1920)
set_option("expand_frame_repr", False)
set_option("max_colwidth", 20)
set_option("io.excel.xlsx.writer", "xlsxwriter")


class Budget:
    """Represents the data-definition of a budget."""

    period: Period
    events: List[Event]

    def __init__(self, period_start, period_end):
        self.period = Period(period_start, period_end)
        self.events = []

    def __repr__(self) -> str:
        return f"Budget(period={self.period!r}, events={self.events!r})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Budget):
            return (
                    (self.period == other.period)
                    and (self.events == other.events)
            )
        return False

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        """Creates and returns new Budget instance from dict data."""

        period_data = data["period"]
        period_start = period_data["start"]
        period_end = period_data["end"]

        result = Budget(period_start, period_end)

        events_data = data["events"]
        for event in events_data:
            description = event["description"]
            amount = event["amount"]
            frequency = event["frequency"]
            result.add_event(description, amount, frequency)

        return result

    @classmethod
    def from_yaml(cls, text: str) -> "Budget":
        """Creates new Budget instance from string containing YAML data."""

        buffer = StringIO(text)
        data = yaml.load(buffer, Loader=yaml.SafeLoader)
        return cls.from_dict(data)

    def add_event(self, description, amount, frequency) -> Event:
        """Create and add Event to the list of events.

        Args:
            description: Event description.
            amount: Event amount.
            frequency: Event frequency.

        Returns:
            The newly-created Event after adding it to the list of events.
        """
        event = Event(description, amount, frequency)
        self.events.append(event)
        return event

    def as_dict(self) -> Dict[str, Union[Dict[str, str], List[Dict[str, str]]]]:
        """Returns dict with the current object's data."""

        return {
            "period": self.period.as_dict(),
            "events": [
                event.as_dict()
                for event
                in self.events
            ]
        }

    def as_yaml(self) -> str:
        """Returns string containing the current budget data in YAML format."""

        data = self.as_dict()
        buffer = StringIO(newline="\n")
        yaml.dump(
            data,
            buffer,
            Dumper=yaml.SafeDumper,
            default_flow_style=False,
            indent=2,
            allow_unicode=True,
            line_break="\n",
            encoding="utf-8",
            sort_keys=False,
        )
        return buffer.getvalue()

    def as_dataframe(self) -> DataFrame:
        """Calculates the daily breakdown and returns the data."""

        data = DataFrame(
            index=date_range(
                start=self.period.start.normalize(),
                end=self.period.end.normalize(),
            )
        )

        for event in self.events:
            event_dates = self.period.generate_datestamps(event.frequency)
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

    def as_csv(self) -> bytes:
        """Returns the daily breakdown data as CSV bytes."""

        buffer = BytesIO()
        data = self.as_dataframe()
        data.to_csv(
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
