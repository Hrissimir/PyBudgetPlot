"""This module defines the data and logic for processing a budget definition."""

from io import StringIO
from typing import Dict, List, Union

import yaml

from pybudgetplot.definitions.event import Event
from pybudgetplot.definitions.period import Period


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

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        """Creates and returns new Budget instance from dict data."""

        period_data = data["period"]
        period_start = period_data["start_date"]
        period_end = period_data["end_date"]

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
