"""Unit-tests for the `pybudgetplot.datamodel.breakdown` module."""

from pathlib import Path
from unittest import TestCase

from pybudgetplot.definitions.breakdown import Breakdown, calculate_breakdown_data
from pybudgetplot.definitions.budget import Budget

SAMPLES_DIR = Path(__file__).parent.joinpath("samples").absolute().resolve()

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


class CalculateBreakdownDataTests(TestCase):
    """Unit-tests for the `calculate_breakdown_data` method."""

    def test_given_bad_param_type_then_raises_type_error(self):
        budget = object()
        with self.assertRaises(TypeError) as ctx:
            calculate_breakdown_data(budget)  # noqa
        expected_args = (budget, Budget, object)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_given_budget_then_returns_correct_data(self):
        budget = BUDGET
        data = calculate_breakdown_data(budget)

        sample_file = SAMPLES_DIR.joinpath("breakdown_dataframe.txt")
        expected = sample_file.read_text("utf-8", errors="surrogateescape")
        actual = str(data)
        self.assertEqual(expected, actual)


class BreakdownTests(TestCase):
    """Unit-tests for the `Breakdown` class."""

    def test_to_csv(self):
        budget = BUDGET
        breakdown = Breakdown(budget)
        sample_file = SAMPLES_DIR.joinpath("breakdown.csv")
        expected_bytes = sample_file.read_bytes()
        expected_str = expected_bytes.decode("utf-8", errors="surrogateescape")
        actual_bytes = breakdown.to_csv()
        actual_str = actual_bytes.decode("utf-8", errors="surrogateescape")
        self.assertEqual(expected_str, actual_str)

    def test_to_xlsx(self):
        budget = BUDGET
        breakdown = Breakdown(budget)

        sample_file = SAMPLES_DIR.joinpath("breakdown.xlsx")
        expected_bytes = sample_file.read_bytes()
        expected_bytes_count = len(expected_bytes)

        # size of sample-file is ~11kb
        self.assertGreaterEqual(expected_bytes_count, 10 * 1000)

        actual_bytes = breakdown.to_xlsx()
        actual_bytes_count = len(actual_bytes)
        self.assertGreaterEqual(expected_bytes_count, 10 * 1000)

        self.assertAlmostEqual(
            expected_bytes_count,
            actual_bytes_count,
            delta=1000
        )
