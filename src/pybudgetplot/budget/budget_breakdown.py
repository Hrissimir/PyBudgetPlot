"""This module defines the logic for dealing with the budged daly breakdowns."""
from io import BytesIO

from pandas import DataFrame, DatetimeIndex, Series, concat, date_range

from pybudgetplot.budget.budget_definition import BudgetDefinition


def calculate_breakdown(budget: BudgetDefinition) -> DataFrame:
    """Calculates the breakdown of the budget's "daily" and "cumulative" totals.

    Args:
        budget: Budget definition.

    Returns:
        DataFrame with the breakdown values.
    """

    breakdown_data = DataFrame(
        index=date_range(budget.period.start, budget.period.end)
    )

    for item in budget.items:
        item_dates = budget.period.generate_dates(item.frequency)
        item_data = DataFrame(
            data={item.description: item.amount},
            index=DatetimeIndex(Series(item_dates, dtype=object))
        )
        breakdown_data = concat([breakdown_data, item_data], axis=1).fillna(0)

    breakdown_data["daily_total"] = breakdown_data.sum(axis=1)
    breakdown_data["cumulative_total"] = breakdown_data["daily_total"].cumsum()
    breakdown_data.index.rename("date", True)
    return breakdown_data


def breakdown_as_csv(budget: BudgetDefinition) -> str:
    """Returns CSV string with the calculated budget breakdown data."""

    buffer = BytesIO()
    data = calculate_breakdown(budget)
    data.to_csv(
        buffer,
        index_label="date",
        encoding="utf-8",
        errors="surrogateescape",
        line_terminator="\n",
        float_format="%.f",
        date_format="%Y-%m-%d",
    )
    return buffer.getvalue().decode("utf-8", errors="surrogateescape")
