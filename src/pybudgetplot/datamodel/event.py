"""This module defines the data and logic for processing an event definition."""
import re
from typing import Any

REGEX_WS_FLAGS = re.DOTALL | re.IGNORECASE | re.MULTILINE
REGEX_WS_PATTERN = re.compile(r"\s+", REGEX_WS_FLAGS)


def parse_string(value: Any) -> str:
    """Converts a value to string.

    Args:
        value: Event description or frequency.

    Returns:
        Non-empty, stripped string with normalized whitespaces or raises.

    Raises:
        TypeError: Raised if the param value is not a string.
        ValueError: Raised if the result value is empty string.
    """

    result = value if isinstance(value, str) else str(value)
    result = REGEX_WS_PATTERN.sub(" ", result).strip()
    if not result:
        raise ValueError(value)
    return result


def parse_amount(value) -> float:
    """Parse amount value to float.

    Args:
        value: Event amount.

    Returns:
        The parsed float or raises.

    Raises:
        ValueError: Raised if the value could not be parsed.
    """

    if isinstance(value, float):
        return value

    try:
        return float(value)
    except Exception as ex:
        raise ValueError(value) from ex


class Event:
    """Represents the data-definition of recurring 'budget-event'."""

    description: str
    amount: float
    frequency: str

    def __init__(self, description, amount, frequency):
        """Class constructor.

        Args:
            description: String with the event description.
            amount: Amount of money that comes or goes with each occurrence.
            frequency: String describing the frequency of the event occurrences.
        """

        self.description = parse_string(description)
        self.amount = parse_amount(amount)
        self.frequency = parse_string(frequency)

    def __repr__(self) -> str:
        return "%s(description=%r, amount=%r, frequency=%r)" % (
            type(self).__name__,
            self.description,
            self.amount,
            self.frequency,
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, Event):
            return (
                    (self.description == other.description)
                    and (self.amount == other.amount)
                    and (self.frequency == other.frequency)
            )
        return False
