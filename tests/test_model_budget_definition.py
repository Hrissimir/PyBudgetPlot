"""Unit-tests for the `pybudgetplot.model.budget_definition` module."""
from unittest import TestCase

from pandas import Timestamp

from pybudgetplot.model.budget_definition import BudgetDefinition, new_budget_definition
from pybudgetplot.model.budget_item import BudgetItem
from pybudgetplot.utils.time_util import Period


class BudgetDefinitionTests(TestCase):
    """Unit-tests for the `budget_definition.new_budget_definition` method."""

    def test_new_budget_definition(self):
        start_param = "2022-01-01"
        end_param = "2022-01-31"

        budget = new_budget_definition(start_param, end_param)
        self.assertIsInstance(budget, BudgetDefinition)

        expected_period = Period(
            Timestamp(year=2022, month=1, day=1).normalize(),
            Timestamp(year=2022, month=1, day=31).normalize(),
        )
        actual_period = budget.period
        self.assertEqual(expected_period, actual_period)

        self.assertIsInstance(budget.items, list)
        self.assertEqual(0, len(budget.items))

    def test_add_item(self):
        budget = new_budget_definition("2022-01-01", "2022-01-31")
        desc = " item \t desc\n"
        amount = "23.50"
        freq = "every \t \n day "
        expected_item = BudgetItem("item desc", 24, "every day")
        actual_item = budget.add_item(desc, amount, freq)
        self.assertIsInstance(actual_item, BudgetItem)
        self.assertEqual(expected_item, actual_item)
        self.assertIn(actual_item, budget.items)
        self.assertEqual(1, len(budget.items))
