"""Unit-tests for the `pybudgetplot.model.budget_definition` module."""
from textwrap import dedent
from unittest import TestCase

from pandas import Timestamp

from pybudgetplot.budget.budget_definition import BudgetDefinition, budget_as_yaml, budget_from_yaml, new_budget
from pybudgetplot.budget.budget_item import BudgetItem
from pybudgetplot.utils.time_util import Period


class NewBudgetDefinitionTests(TestCase):
    """Unit-tests for the `budget_definition.new_budget_definition` method."""

    def test_new_budget_definition(self):
        start_param = "2022-01-01"
        end_param = "2022-01-31"

        budget = new_budget(start_param, end_param)
        self.assertIsInstance(budget, BudgetDefinition)

        expected_period = Period(
            Timestamp(year=2022, month=1, day=1).normalize(),
            Timestamp(year=2022, month=1, day=31).normalize(),
        )
        actual_period = budget.period
        self.assertEqual(expected_period, actual_period)

        self.assertIsInstance(budget.items, list)
        self.assertEqual(0, len(budget.items))


class AddItemTests(TestCase):
    """Unit-tests for the `BudgetDefinition.add_item` method."""

    def test_add_item(self):
        budget = new_budget("2022-01-01", "2022-01-31")
        desc = " item \t desc\n"
        amount = "23.50"
        freq = "every \t \n day "
        expected_item = BudgetItem("item desc", 24, "every day")
        actual_item = budget.add_item(desc, amount, freq)
        self.assertIsInstance(actual_item, BudgetItem)
        self.assertEqual(expected_item, actual_item)
        self.assertIn(actual_item, budget.items)
        self.assertEqual(1, len(budget.items))


class BudgetAsYamlTests(TestCase):
    """Unit-tests for the `budget_definition.budget_as_yaml` method."""

    def test_budget_as_yaml(self):
        budget = new_budget("2021-12-31", "2022-01-05")
        budget.add_item("cash", 200, "2021-12-31")
        budget.add_item("food", -5, "every day starting 2022-01-01")
        budget.add_item(
            "commute", -1, "every day starting 2022-01-02 until 2022-01-04"
        )

        expected = dedent(
            """\
            PERIOD:
                start: '2021-12-31'
                end: '2022-01-05'
            ITEMS:
                cash:
                    amount: 200
                    frequency: '2021-12-31'
                food:
                    amount: -5
                    frequency: every day starting 2022-01-01
                commute:
                    amount: -1
                    frequency: every day starting 2022-01-02 until 2022-01-04
            """
        )
        actual = budget_as_yaml(budget)
        self.assertEqual(expected, actual)


class BudgetFromYamlTests(TestCase):
    """Unit-tests for the `budget_definition.budget_from_yaml` method."""

    def test_budget_from_yaml(self):
        text = dedent(
            """\
            PERIOD:
                start: '2021-12-31'
                end: '2022-01-05'
            ITEMS:
                cash:
                    amount: 200
                    frequency: '2021-12-31'
                food:
                    amount: -5
                    frequency: every day starting 2022-01-01
                commute:
                    amount: -1
                    frequency: every day starting 2022-01-02 until 2022-01-04
            """
        )

        expected = new_budget("2021-12-31", "2022-01-05")
        expected.add_item("cash", 200, "2021-12-31")
        expected.add_item("food", -5, "every day starting 2022-01-01")
        expected.add_item(
            "commute", -1, "every day starting 2022-01-02 until 2022-01-04"
        )

        actual = budget_from_yaml(text)
        self.assertEqual(expected, actual)
