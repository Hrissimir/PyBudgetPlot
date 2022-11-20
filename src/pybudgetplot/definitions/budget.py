"""This module defines the data and logic for processing a budget definition."""

import logging
from io import StringIO
from typing import List, NamedTuple

import yaml

from pybudgetplot.definitions.event import Event
from pybudgetplot.definitions.period import Period

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class Budget(NamedTuple):
    """Represents the budget definition data."""

    period: Period
    events: List[Event]

    @classmethod
    def new(cls, period_start, period_end) -> "Budget":
        """Helper method for creating new Budget instances.

        Args:
            period_start: Value for the budget's period start-date.
            period_end: Value for the budget's period end-date.

        Returns:
            Budget instance for the Period and empty list of events.
        """

        _log.debug(
            "Budget.new - period_start: %r, period_end: %r",
            period_start,
            period_end
        )
        period = Period.new(period_start, period_end)
        events = []
        result = cls(period, events)
        _log.debug("Budget.new - result: %r", result)
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        """Creates and returns new Budget instance from dict data."""

        period_data = data["period"]
        period_start = period_data["start_date"]
        period_end = period_data["end_date"]
        result = cls.new(period_start, period_end)

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
        """Creates new Event and adds it to the current list of events.

        Args:
            description: Event description.
            amount: Event amount.
            frequency: Event frequency.

        Returns:
            The newly-created Event after adding it to the list of events.
        """

        _log.debug(
            "add_event - description: %r, amount: %r, frequency: %r",
            description,
            amount,
            frequency
        )
        event = Event.new(description, amount, frequency)
        self.events.append(event)
        return event

    def as_dict(self) -> dict:
        """Returns dict with the current budget's data."""

        return {
            "period": self.period.as_dict(),
            "events": [event.as_dict() for event in self.events]
        }

    def as_yaml(self) -> str:
        """Returns string containing the current budget data in YAML format."""

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
