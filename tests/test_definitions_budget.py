"""Unit-tests for the `pybudgetplot.definitions.budget` module."""
from pathlib import Path
from unittest import TestCase

from pandas import Timestamp

from pybudgetplot.definitions.budget import Budget
from pybudgetplot.definitions.event import Event
from pybudgetplot.definitions.period import Period

BUDGET = Budget("2020-11-01", "2020-12-31")
BUDGET.add_event("Salary", 1300, "Every Month starting 2020-11-03")
BUDGET.add_event("Rent", -450, "Every Month starting 2020-11-15")
BUDGET.add_event("WaterBill", -30, "Every Month starting 2020-11-08")
BUDGET.add_event("PowerBill", -60, "Every Month starting 2020-11-07")
BUDGET.add_event("PhoneBill", -25, "Every Month starting 2020-11-06")
BUDGET.add_event("Food", -15, "Every day")
BUDGET.add_event("Commute", -5, "Every WeekDay")
BUDGET.add_event("Tobacco", -15, "Every Week")
BUDGET.add_event("Snacks", -10, "Every 3 Days")
BUDGET.add_event("Party", -20, "Every 2 weeks on Friday and Saturday")
BUDGET.add_event("Cash", 200, "2020-11-01")

SAMPLES_DIR = Path(__file__).parent.joinpath("samples").absolute().resolve()


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

    def test_from_dict(self):
        data = {
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

        expected = Budget("2022-01-01", "2022-01-31")
        expected.add_event("event desc", 23.5, "every day")
        actual = Budget.from_dict(data)
        self.assertEqual(expected, actual)

    def test_as_yaml(self):
        sample_file = SAMPLES_DIR.joinpath("budget.yaml")
        expected_bytes = sample_file.read_bytes()
        expected_str = expected_bytes.decode("utf-8", errors="surrogateescape")
        actual_str = BUDGET.as_yaml()
        self.assertEqual(expected_str, actual_str)

    def test_from_yaml(self):
        yaml_file = SAMPLES_DIR.joinpath("budget.yaml")
        yaml_bytes = yaml_file.read_bytes()
        yaml_str = yaml_bytes.decode("utf-8", errors="surrogateescape")
        expected = BUDGET
        actual = Budget.from_yaml(yaml_str)
        self.assertEqual(expected, actual)

    def test_as_csv(self):
        sample_file = SAMPLES_DIR.joinpath("budget.csv")
        expected_bytes = sample_file.read_bytes()
        expected_str = expected_bytes.decode("utf-8", errors="surrogateescape")
        actual_bytes = BUDGET.as_csv()
        actual_str = actual_bytes.decode("utf-8", errors="surrogateescape")
        self.assertEqual(expected_str, actual_str)
