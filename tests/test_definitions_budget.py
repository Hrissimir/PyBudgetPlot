"""Unit-tests for the `pybudgetplot.definitions.budget` module."""
from textwrap import dedent
from unittest import TestCase

from pandas import Timestamp

from pybudgetplot.definitions.budget import Budget
from pybudgetplot.definitions.event import Event
from pybudgetplot.definitions.period import Period


class BudgetTests(TestCase):
    """Unit-tests for the `Budget` class."""

    def test_constructor(self):
        budget = Budget("2022-01-01", "2022-01-31")

        self.assertIsInstance(budget.period, Period)
        self.assertIsInstance(budget.events, list)

        expected_period = Period(
            Timestamp(year=2022, month=1, day=1),
            Timestamp(year=2022, month=1, day=31)
        )
        actual_period = budget.period
        self.assertEqual(expected_period, actual_period)

        expected_events = []
        actual_events = budget.events
        self.assertListEqual(expected_events, actual_events)

    def test_repr(self):
        budget = Budget("2022-01-01", "2022-01-31")
        budget.add_event("event desc", 23.5, "every day")
        expected = (
            "Budget("
            f"period={repr(budget.period)}, events={repr(budget.events)}"
            ")"
        )
        actual = repr(budget)
        self.assertEqual(expected, actual)

    def test_eq(self):
        current = Budget("2022-01-01", "2022-01-31")
        other = object()
        self.assertFalse(current == other)

    def test_add_event(self):
        budget = Budget("2022-01-01", "2022-01-31")
        desc = " event \t desc\n"
        amount = "23.50"
        freq = "every \t \n day "
        expected_event = Event("event desc", 23.50, "every day")
        actual_event = budget.add_event(desc, amount, freq)
        self.assertEqual(expected_event, actual_event)
        self.assertIn(actual_event, budget.events)
        self.assertListEqual([actual_event], budget.events)

    def test_as_dict(self):
        budget = Budget("2022-01-01", "2022-01-31")
        budget.add_event("event desc", 23.5, "every day")
        expected = {
            "period": {
                "start": "2022-01-01",
                "end": "2022-01-31",
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
        budget = Budget("2022-01-01", "2022-12-31")
        budget.add_event("salary", 2345.6, "every month")
        expected = dedent(
            """\
            period:
              start: '2022-01-01'
              end: '2022-12-31'
            events:
            - description: salary
              amount: '2345.60'
              frequency: every month
            """
        )
        actual = budget.as_yaml()
        self.assertEqual(expected, actual)

    def test_from_dict(self):
        data = {
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

        expected = Budget("2022-01-01", "2022-01-31")
        expected.add_event("event desc", 23.5, "every day")
        actual = Budget.from_dict(data)
        self.assertEqual(expected, actual)

    def test_from_yaml(self):
        text = dedent(
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

        expected = Budget("2022-01-01", "2022-12-31")
        expected.add_event("salary", 2345.6, "every month")
        actual = Budget.from_yaml(text)
        self.assertEqual(expected, actual)
