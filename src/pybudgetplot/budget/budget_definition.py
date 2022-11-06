"""This module defines the logic for dealing with budget definitions."""
from io import StringIO
from typing import List, NamedTuple

import yaml

from pybudgetplot.budget.budget_item import BudgetItem, new_budget_item
from pybudgetplot.utils.time_util import Period, date_period


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

        item = new_budget_item(description, amount, frequency)
        self.items.append(item)
        return item


def new_budget(period_start, period_end) -> BudgetDefinition:
    """Creates and returns a new budget definition for the given period.

    Args:
        period_start: Start-date for the budget's period.
        period_end: End-date for the budget's period.

    Returns:
        New BudgetDefinition instance for the period, with empty list of items.
    """

    period = date_period(period_start, period_end)
    items = []
    budget = BudgetDefinition(period, items)
    return budget


def budget_as_dict(budget: BudgetDefinition) -> dict:
    """Returns a dict with the budget definition data."""

    period_dict = {
        "start": budget.period.start.date().isoformat(),
        "end": budget.period.end.date().isoformat()
    }

    items_dict = {
        item.description: {
            "amount": item.amount,
            "frequency": item.frequency
        }
        for item
        in budget.items
    }

    budget_dict = {
        "PERIOD": period_dict,
        "ITEMS": items_dict,
    }

    return budget_dict


def budget_as_yaml(budget: BudgetDefinition) -> str:
    """Formats the budged definition in YAML format."""

    budget_dict = budget_as_dict(budget)

    buffer = StringIO(newline="\n")
    yaml.dump(
        budget_dict,
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


def budget_from_dict(budget_data: dict) -> BudgetDefinition:
    """Creates BudgetDefinition instance from data dict."""

    period_data = budget_data["PERIOD"]
    period_start = period_data["start"]
    period_end = period_data["end"]
    budget = new_budget(period_start, period_end)

    items_data = budget_data["ITEMS"]
    for item_description, item_details in items_data.items():
        item_amount = item_details["amount"]
        item_frequency = item_details["frequency"]
        budget.add_item(item_description, item_amount, item_frequency)

    return budget


def budget_from_yaml(text) -> BudgetDefinition:
    """Parses and returns BudgetDefinition from string with YAML text."""

    buffer = StringIO(text)
    budget_data = yaml.load(buffer, Loader=yaml.SafeLoader)
    return budget_from_dict(budget_data)
