"""Unit-tests for the `pybudgetplot.utils.plot_util` module."""
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from pybudgetplot.datamodel.budget import Budget
from pybudgetplot.utils.file_util import read_str
from pybudgetplot.utils.plot_util import plot_budget

SAMPLES_DIR = Path(__file__).parent.joinpath("samples").absolute().resolve()

BUDGET_YAML = read_str(SAMPLES_DIR.joinpath("budget.yaml"))

BUDGET = Budget.from_yaml(BUDGET_YAML)


class PlotBudgetTests(TestCase):
    """Unit-tests for the `plot_budget` method."""

    @patch("matplotlib.pyplot.show", autospec=True)
    @patch("matplotlib.pyplot.savefig", autospec=True)
    def test_plot_both_to_file_and_interactive(
            self,
            mock_savefig: MagicMock,
            mock_show: MagicMock,
    ):
        file = Path(__file__).parent.joinpath("graph.png")
        plot_budget(BUDGET, file=file, interactive=True)

        expected_savefig_calls = [call(file)]
        actual_savefig_calls = mock_savefig.mock_calls
        self.assertListEqual(expected_savefig_calls, actual_savefig_calls)

        mock_show.assert_called_once_with()

    @patch("matplotlib.pyplot.show", autospec=True)
    @patch("matplotlib.pyplot.savefig", autospec=True)
    def test_plot_interactive_only(
            self,
            mock_savefig: MagicMock,
            mock_show: MagicMock,
    ):
        plot_budget(BUDGET, interactive=True)
        mock_savefig.assert_not_called()
        mock_show.assert_called_once_with()
