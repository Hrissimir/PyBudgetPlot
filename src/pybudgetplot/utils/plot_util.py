"""Helper module for plotting a budget to file or interactively."""
import logging

from matplotlib import pyplot
from pandas import DataFrame
from pandas.plotting import register_matplotlib_converters

from pybudgetplot.datamodel.budget import Budget

logging.getLogger("PIL.PngImagePlugin").disabled = True
logging.getLogger("matplotlib.font_manager").disabled = True

register_matplotlib_converters()

_FIG_NUM = 42
_FIG_WIDTH = 16
_FIG_HEIGHT = 9

_LABEL_DAILY = "Daily Total"
_LABEL_CUMULATIVE = "Cumulative Total"


def _draw_figure(data: DataFrame):
    """Draws graph of the 'daily_total' and 'cumulative_total' data values."""

    pyplot.figure(num=_FIG_NUM, figsize=(_FIG_WIDTH, _FIG_HEIGHT), clear=True)
    pyplot.plot(data.index, data.cumulative_total, label=_LABEL_CUMULATIVE)
    pyplot.plot(data.index, data.daily_total, label=_LABEL_DAILY)
    pyplot.legend()


def plot_budget(budget: Budget, *, file=None, interactive=False):
    """Plots the budget to file or interactively or both."""

    data = budget.as_dataframe()

    _draw_figure(data)

    if file is not None:
        pyplot.savefig(file)

    if interactive:
        pyplot.show()
