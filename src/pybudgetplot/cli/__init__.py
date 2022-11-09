# SPDX-FileCopyrightText: 2022-present Hrissimir <hrisimir.dakov@gmail.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path
from textwrap import dedent

import click

from pybudgetplot.model.budget_breakdown import breakdown_as_csv, calculate_breakdown
from pybudgetplot.model.budget_definition import from_yaml
from pybudgetplot.utils import plot_util

from ..__about__ import __version__  # pylint: disable=relative-beyond-top-level
from ..datamodel import as_xlsx

SAMPLE_YAML = dedent(
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


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(
    version=__version__,
    prog_name="PyBudgetPlot",
)
def cli():
    """Composite CLI command for managing a 'budget-definition' file."""


@cli.command()
@click.argument(
    "file",
    type=click.File(
        mode="w",
        encoding="utf-8",
        errors="surrogateescape",
        atomic=True,
    ),
    required=False,
    default="-",
)
def init(file):
    """Initialize a budget definition file with sample contents."""

    file.write(SAMPLE_YAML)


@cli.command()
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=False,
    help="Enter interactive plot mode.",
)
@click.option(
    "-p",
    "--png",
    is_flag=True,
    default=False,
    help="Write .PNG with the graph next to definition file.",
)
@click.option(
    "-c",
    "--csv",
    is_flag=True,
    default=False,
    help="Write .CSV with the breakdown next to definition file.",
)
@click.option(
    "-x",
    "--xlsx",
    is_flag=True,
    default=False,
    help="Write .XLSX with the breakdown next to definition file.",
)
@click.argument(
    "yaml_file",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        allow_dash=False,
        path_type=Path
    ),
    required=True,
)
def plot(interactive: bool, png: bool, csv: bool, xlsx: bool, yaml_file: Path):
    """Plot a budget-definition .yaml file."""

    file = yaml_file.absolute().resolve()
    text = file.read_text(encoding="utf-8", errors="surrogateescape")
    budget = from_yaml(text)
    breakdown = calculate_breakdown(budget)

    folder = file.parent

    if csv:
        csv_file = folder.joinpath(f"{file.stem}.csv")
        csv_bytes = breakdown_as_csv(breakdown)
        csv_file.write_bytes(csv_bytes)

    if xlsx:
        xlsx_file = folder.joinpath(f"{file.stem}.xlsx")
        xlsx_bytes = as_xlsx(breakdown)
        xlsx_file.write_bytes(xlsx_bytes)

    if (not interactive) and (not png):
        return

    plot_util.plot_graph(breakdown)

    if png:
        png_file = folder.joinpath(f"{file.stem}.png")
        plot_util.save_graph(png_file)

    if interactive:
        plot_util.show_graph()
