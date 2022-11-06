"""Unit-tests for the `pybudgetplot.budget.budget_breakdown` module."""
from textwrap import dedent
from unittest import TestCase

from pandas import DataFrame

from pybudgetplot.budget.budget_breakdown import breakdown_as_csv, calculate_breakdown
from pybudgetplot.budget.budget_definition import budget_from_yaml

BUDGET_YAML = dedent(
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


class CalculateBreakdownTests(TestCase):
    """Unit-tests for `budget_breakdown.calculate_breakdown` method."""

    def test_calculate_budget_breakdown(self):
        budget = budget_from_yaml(BUDGET_YAML)
        breakdown = calculate_breakdown(budget)
        self.assertIsInstance(breakdown, DataFrame)

        expected = dedent(
            # pylint: disable=trailing-whitespace
            """\
                         cash  food  commute  daily_total  cumulative_total
            date
            2021-12-31  200.0   0.0      0.0        200.0             200.0
            2022-01-01    0.0  -5.0      0.0         -5.0             195.0
            2022-01-02    0.0  -5.0     -1.0         -6.0             189.0
            2022-01-03    0.0  -5.0     -1.0         -6.0             183.0
            2022-01-04    0.0  -5.0     -1.0         -6.0             177.0
            2022-01-05    0.0  -5.0      0.0         -5.0             172.0"""
        )
        actual = "\n".join([
            line.rstrip()
            for line
            in str(breakdown).splitlines(False)
        ])
        self.assertEqual(expected, actual)


class BreakdownAsCsvTests(TestCase):
    """Unit-tests for `budget_breakdown.breakdown_as_csv` method."""

    def test_breakdown_as_csv(self):
        budget = budget_from_yaml(BUDGET_YAML)
        expected = dedent(
            """\
            date,cash,food,commute,daily_total,cumulative_total
            2021-12-31,200,0,0,200,200
            2022-01-01,0,-5,0,-5,195
            2022-01-02,0,-5,-1,-6,189
            2022-01-03,0,-5,-1,-6,183
            2022-01-04,0,-5,-1,-6,177
            2022-01-05,0,-5,0,-5,172
            """)
        actual = breakdown_as_csv(budget)
        self.assertEqual(expected, actual)
