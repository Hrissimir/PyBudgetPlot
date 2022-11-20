"""Unit-tests for the `pybudgetplot.definitions.budget` module."""

from textwrap import dedent
from unittest import TestCase

from pandas import Timestamp

from pybudgetplot.definitions.budget import Budget
from pybudgetplot.definitions.event import Event
from pybudgetplot.definitions.period import Period


class BudgetTests(TestCase):
    """Unit-tests for the `Budget` class."""

    def test_new(self):
        expected = Budget(
            period=Period(
                start_date=Timestamp(year=2022, month=1, day=1),
                end_date=Timestamp(year=2022, month=1, day=31)
            ),
            events=[]
        )
        actual = Budget.new("2022-01-01", "2022-01-31")
        self.assertEqual(expected, actual)

    def test_add_event(self):
        budget = Budget.new("2022-01-01", "2022-01-31")
        desc = " event \t desc\n"
        amount = "23.50"
        freq = "every \t \n day "
        expected_event = Event("event desc", 23.50, "every day")
        actual_event = budget.add_event(desc, amount, freq)
        self.assertEqual(expected_event, actual_event)
        self.assertIn(actual_event, budget.events)
        self.assertListEqual([actual_event], budget.events)

    def test_as_dict(self):
        budget = Budget.new("2022-01-01", "2022-01-31")
        budget.add_event("event desc", 23.5, "every day")
        expected = {
            "period": {
                "start_date": "2022-01-01",
                "end_date": "2022-01-31",
            },
            "events": [
                {
                    "description": "event desc",
                    "amount": "23.50",
                    "frequency": "every day"
                },
            ],
        }
        actual = budget.as_dict()
        self.assertDictEqual(expected, actual)

    def test_as_yaml(self):
        budget = Budget.new("2022-01-01", "2022-12-31")
        budget.add_event("salary", 2345.6, "every month")
        expected = dedent(
            """\
            period:
                start_date: '2022-01-01'
                end_date: '2022-12-31'
            events:
            -   description: salary
                amount: '2345.60'
                frequency: every month
            """
        )
        actual = budget.as_yaml()
        self.assertEqual(expected, actual)
