"""This module defines the data and logic for processing an event definition."""
import logging
import re
from typing import NamedTuple

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def normalize_string(value) -> str:
    """Normalize a string value.

    Args:
        value: Usually a sentence containing an event description or frequency.

    Returns:
        Non-empty, stripped string with normalized whitespace.

    Raises:
        TypeError: Raised if the value is not a string instance.
        ValueError: Raised if the resulting string is empty.
    """

    _log.debug("normalize_string - value: '%s'", value)

    if not isinstance(value, str):
        _log.warning("normalize_string - bad param type!")
        raise TypeError(value, str, type(value))

    result = re.sub(r"\s+", " ", value).strip()
    if not result:
        _log.warning("normalize_string - the resulting string is empty!")
        raise ValueError(value)

    _log.debug("normalize_string - result: '%s'", result)
    return result


def parse_amount(value) -> float:
    """Parse value of event amount.

    Args:
        value: Any value parsable to float.

    Returns:
        Float with the parsed value or raises.

    Raises:
        ValueError: Raised if the value could not be parsed to float.
    """

    _log.debug("parse_amount - value: '%s'", value)
    try:
        if isinstance(value, float):
            result = value
        else:
            result = float(value)
        _log.debug("parse_amount - result: '%.2f'", result)
        return result
    except Exception as ex:
        _log.warning("parse_amount - error: '%s'", ex)
        raise ValueError(value) from ex


class Event(NamedTuple):
    """Represents the definition of a budget event."""

    description: str
    amount: float
    frequency: str

    def as_dict(self) -> dict:
        """Returns dict with the current event data."""

        return {
            "description": self.description,
            "amount": f"{self.amount:.2f}",
            "frequency": self.frequency
        }


def new_event(description, amount, frequency) -> Event:
    """Helper method for creation of new Event instances.

    This method processes the args before passing them to Event constructor.

    Args:
        description: Short description of the event.
        amount: Amount of money that comes or goes with each event occurrence.
        frequency: Frequency of the event occurrences.

    Returns:
        Event instance.
    """

    _log.debug(
        "new_event - description: '%s', amount: '%s', frequency: '%s'",
        description,
        amount,
        frequency
    )

    event_description = normalize_string(description)
    event_amount = parse_amount(amount)
    event_frequency = normalize_string(frequency)
    result = Event(event_description, event_amount, event_frequency)
    _log.debug("new_event - result: '%s'", result)
    return result
