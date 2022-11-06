"""This module defines the logic for dealing with single budget-item."""
import logging
import re
from decimal import ROUND_HALF_UP, Decimal
from typing import NamedTuple

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def parse_string(value) -> str:
    """Parse value to non-empty and stripped string.

    Args:
        value: String instance.

    Returns:
        Non-empty stripped string or raises.

    Raises:
        TypeError: raised when the value is not string instance.
        ValueError: raised when the resulting string is empty.
    """

    if not isinstance(value, str):
        raise TypeError(value, str, type(value))

    normalized_spacing = re.sub(r"\s+", " ", value)
    resulting_string = normalized_spacing.strip()

    if not resulting_string:
        raise ValueError(value)

    return resulting_string


def parse_int(value) -> int:
    """Attempts to parse int from any value.

    Args:
        value: Any value that can be parsed to int.

    Returns:
        Int with the parsed value upon success, raises otherwise.

    Raises:
        ValueError: raised if the value could not be parsed.
    """

    if isinstance(value, int):
        return value

    try:
        str_value = parse_string(str(value))
        decimal_value = Decimal(str_value).to_integral_value(ROUND_HALF_UP)
        return int(decimal_value)
    except Exception as ex:
        raise ValueError(value) from ex


class BudgetItem(NamedTuple):
    """Represents the definition of a single, recurring item from the budget."""

    description: str
    amount: int
    frequency: str


def new_budget_item(description, amount, frequency) -> BudgetItem:
    """Creates and returns a new BudgetItem instance with the given details.

    Validates the params before actually creating the object.

    Args:
        description: The item's description (can't be empty).
        amount: The item's amount (converted to int).
        frequency: The item's frequency (can't be empty).
    """

    _log.debug(
        "new_budget_item - description: '%r', amount: '%r', frequency: '%r'",
        description,
        amount,
        frequency
    )
    description_value = parse_string(description)
    amount_value = parse_int(amount)
    frequency_value = parse_string(frequency)
    item = BudgetItem(description_value, amount_value, frequency_value)
    _log.info("new_budget_item - created: '%r'", item)
    return item
