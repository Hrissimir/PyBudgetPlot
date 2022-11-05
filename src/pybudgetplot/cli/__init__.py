# SPDX-FileCopyrightText: 2022-present Hrissimir <hrisimir.dakov@gmail.com>
#
# SPDX-License-Identifier: MIT
import click

from ..__about__ import __version__


@click.group(context_settings={'help_option_names': ['-h', '--help']}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name='PyBudgetPlot')
@click.pass_context
def pybudgetplot(ctx: click.Context):  # pylint: disable=unused-argument
    click.echo('Hello world!')
