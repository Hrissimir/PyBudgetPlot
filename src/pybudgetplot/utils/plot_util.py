import logging
from pathlib import Path
from typing import Optional

from matplotlib import pyplot
from pandas import DataFrame
from pandas.plotting import register_matplotlib_converters

logging.getLogger("PIL.PngImagePlugin").disabled = True
logging.getLogger("matplotlib.font_manager").disabled = True
register_matplotlib_converters()

GRAPH_SIZE = (16, 9)
GRAPH_LABEL_DAILY = "Daily Total"
GRAPH_LABEL_CUMULATIVE = "Cumulative Total"

_graph: Optional[pyplot.Figure] = None


def plot_graph(data: DataFrame):
    """Plots a graph from the given budget breakdown data."""

    global _graph
    _graph = pyplot.figure(figsize=GRAPH_SIZE)
    pyplot.plot(data.index, data.daily_total, label=GRAPH_LABEL_DAILY)
    pyplot.plot(data.index, data.cumulative_total, label=GRAPH_LABEL_CUMULATIVE)
    pyplot.legend()


def save_graph(file: Path):
    """Writes the currently plotted graph to the file."""

    global _graph  # pylint: disable=global-variable-not-assigned
    _graph.savefig(file)


def show_graph():
    """Shows the currently plotted graph in interactive mode."""

    pyplot.show()
