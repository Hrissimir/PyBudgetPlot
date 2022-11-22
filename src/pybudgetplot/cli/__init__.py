# SPDX-FileCopyrightText: 2022-present Hrissimir <hrisimir.dakov@gmail.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path

import click

from pybudgetplot.datamodel.budget import Budget
from pybudgetplot.utils.file_util import read_str, write_bytes, write_str
from pybudgetplot.utils.plot_util import plot_budget

from ..__about__ import __version__  # pylint: disable=relative-beyond-top-level

SAMPLE_BUDGET = Budget("2020-11-01", "2020-12-31")
SAMPLE_BUDGET.add_event("Cash", 200, "2020-11-01")
SAMPLE_BUDGET.add_event("Salary", 1300, "Every Month starting 2020-11-03")
SAMPLE_BUDGET.add_event("Rent", -450, "Every Month starting 2020-11-15")
SAMPLE_BUDGET.add_event("WaterBill", -30, "Every Month starting 2020-11-08")
SAMPLE_BUDGET.add_event("PowerBill", -60, "Every Month starting 2020-11-07")
SAMPLE_BUDGET.add_event("PhoneBill", -25, "Every Month starting 2020-11-06")
SAMPLE_BUDGET.add_event("Food", -15, "Every day")
SAMPLE_BUDGET.add_event("Commute", -5, "Every WeekDay")
SAMPLE_BUDGET.add_event("Tobacco", -15, "Every Week")
SAMPLE_BUDGET.add_event("Snacks", -10, "Every 3 Days")
SAMPLE_BUDGET.add_event("Party", -20, "Every 2 weeks on Friday and Saturday")


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

    sample_yaml = SAMPLE_BUDGET.as_yaml()
    click.echo(sample_yaml, file=file)


@cli.command()
@click.option(
    "-c",
    "--csv",
    is_flag=True,
    default=False,
    help="Write .CSV with the breakdown next to definition file.",
)
@click.option(
    "-p",
    "--png",
    is_flag=True,
    default=False,
    help="Write .PNG with the graph next to definition file.",
)
@click.option(
    "-t",
    "--txt",
    is_flag=True,
    default=False,
    help="Write .TXT with the breakdown next to definition file.",
)
@click.option(
    "-x",
    "--xlsx",
    is_flag=True,
    default=False,
    help="Write .XLSX with the breakdown next to definition file.",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=False,
    help="Enter interactive plot mode.",
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
        path_type=Path,
    ),
    required=True,
)
def plot(
    csv: bool, png: bool, txt: bool, xlsx: bool, interactive: bool, yaml_file: Path
):
    """Plot a budget-definition .yaml file."""

    file = Path(yaml_file).absolute().resolve(strict=True)
    folder = file.parent

    text = read_str(file)
    budget = Budget.from_yaml(text)

    if csv:
        csv_file = folder.joinpath(f"{file.stem}.csv")
        csv_bytes = budget.to_csv()
        write_bytes(csv_file, csv_bytes)

    if txt:
        txt_file = folder.joinpath(f"{file.stem}.txt")
        write_str(txt_file, str(budget.as_dataframe()))

    if xlsx:
        xlsx_file = folder.joinpath(f"{file.stem}.xlsx")
        xlsx_bytes = budget.to_xlsx()
        write_bytes(xlsx_file, xlsx_bytes)

    if png:
        png_file = folder.joinpath(f"{file.stem}.png")
    else:
        png_file = None

    if interactive or png_file:
        plot_budget(budget, interactive=interactive, file=png_file)
