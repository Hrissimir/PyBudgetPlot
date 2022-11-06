"""This module defines the logic for dealing with budget definitions."""
import logging
from typing import List, NamedTuple

from pybudgetplot.model.budget_item import BudgetItem, new_budget_item
from pybudgetplot.utils.time_util import Period, date_period

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class BudgetDefinition(NamedTuple):
    """Represents the definition of a budget for a given period."""

    period: Period
    items: List[BudgetItem]

    def add_item(self, description, amount, frequency) -> BudgetItem:
        """Creates a new BudgetItem instance and adds it to the list of items.

        Args:
            description: Item description (processed and stripped).
            amount: Item amount (processed and converted to int).
            frequency: Item frequency (processed and stripped).

        Returns:
            The newly created BudgetItem instance after adding it to the list.
        """

        _log.debug(
            "add_item - description: '%r', amount: '%r', frequency: '%r'",
            description,
            amount,
            frequency
        )
        item = new_budget_item(description, amount, frequency)
        self.items.append(item)
        _log.info("add_item - added: %s", item)
        return item


def new_budget_definition(period_start, period_end) -> BudgetDefinition:
    """Creates and returns a new budget definition for the given period.

    Args:
        period_start: Start-date for the budget's period.
        period_end: End-date for the budget's period.

    Returns:
        New BudgetDefinition instance for the period, with empty list of items.
    """

    _log.debug(
        "new_budget_definition - period_start: '%r', period_end: '%r'",
        period_start,
        period_end
    )
    period = date_period(period_start, period_end)
    items = []
    budget = BudgetDefinition(period, items)
    _log.info("new_budget_definition - created: %r", budget)
    return budget


def main():
    pass


if __name__ == "__main__":
    main()
