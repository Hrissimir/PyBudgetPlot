# PyBudgetPlot

|         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CI/CD   | [![CI - Test](https://github.com/Hrissimir/PyBudgetPlot/actions/workflows/test.yml/badge.svg)](https://github.com/Hrissimir/PyBudgetPlot/actions/workflows/test.yml)                                                                                                                                                                                                                                                                                                                                                                                           |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/pybudgetplot.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/pybudgetplot) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pybudgetplot.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/pybudgetplot)                                                                                                                                                                                                                                              |
| Meta    | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint) [![imports - isort](https://img.shields.io/badge/imports-isort-ef8336.svg)](https://github.com/pycqa/isort) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) |

-----

**Table of Contents**

- [Introduction](#introduction)
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [CLI Commands](#cli-commands)
- [License](#license)

-----

## Introduction

This project was inspired by the *"Personal finance with Python"* book.

It'll help you to get the answers to the following list of questions (and more):

* I want to visit Greece during September, will I have saved-up enough to go?
* I want to buy a car, but how much time do I need to save-up with my lifestyle?
    * What about if I change my current lifestyle a bit?
* Got offered a slightly better salary than my current, should I take it or not?
    * I'll have different expenses, what's the total net-worth change then?
    * Are those 200 bucks change in salary worth the trouble at all?
    * What about if I work somewhere for smaller salary but fewer expenses too?
* I want to lead the following lifestyle, how much money should I earn to do so?
* Any other question concerned about how-much money you'll have on a given date.

While *"some logic"* from the *"Personal finance with Python"* book is reused,

the source-code and the contents of the produced outputs are *quite different*.

-----

## Overview

All the project's functionality revolves around a *'budget-definition'* file.

The *definition* file is used for storing the *budget data* in YAML format.

The *budget data* consists of two components:

* Period
    * Represents list of all dates that fall in the *scope* of the *budget*.
    * Defined by a *start-date* and an *end-date* values in ISO-format.
* Events
    * Represents list of *recurring* events of *spending or receiving money*.
    * Each *Event* is defined by *description*, *amount* and *frequency*.

The *definition* file is used as input for the following operations:

* Calculation of *daily* and *cumulative* totals for each date in the period.
    * The output can be saved as CSV or dynamic XLSX file that's using formulas.
* Plotting (line-chart) graph visualization of the daily and cumulative totals.
    * The output can be saved as PNG or an *interactive* plotter can be opened.

Two budgets and their outputs are included in the ['examples'](examples) dir.

The difference between 1300 and 1500 salary in the long-term can be surprising.


-----

## Installation

The project can be installed from PyPI using the following commands:

```shell
# Windows - open admin-level CMD and run:
pip install pybudgetplot

# Linux / MacOS - open user-level Terminal and run:
pip3 install --user pybudgetplot
```

-----

## Usage

### 1. Init a sample budget-definition file.

```shell
# generates budget.yaml file in the current dir
budget init budget.yaml
```

### 2. Update the file as per your needs and save the changes.

### 3. Generate outputs in one or all of the supported formats.

```shell
# generates budget.csv, budget.png, budget.txt, budget.xlsx files in current dir
budget plot -c -p -t -x budget.yaml
```

-----

## CLI Commands

```shell
# ------------------------------------------------------------------------------
# see the 'budget' command help
# ------------------------------------------------------------------------------
> budget -h

    Usage: budget [OPTIONS] COMMAND [ARGS]...

      Composite CLI command for managing a 'budget-definition' file.

    Options:
      --version   Show the version and exit.
      -h, --help  Show this message and exit.

    Commands:
      init  Initialize a budget definition file with sample contents.
      plot  Plot a budget-definition .yaml file.

# ------------------------------------------------------------------------------
# see the 'budget init' command help
# ------------------------------------------------------------------------------
> budget init -h

    Usage: budget init [OPTIONS] [FILE]

      Initialize a budget definition file with sample contents.

    Options:
      -h, --help  Show this message and exit.

# ------------------------------------------------------------------------------
# see the 'budget plot' command help
# ------------------------------------------------------------------------------
> budget plot -h

    Usage: budget plot [OPTIONS] YAML_FILE

      Plot a budget-definition .yaml file.

    Options:
      -c, --csv          Write .CSV with the breakdown next to definition file.
      -p, --png          Write .PNG with the graph next to definition file.
      -t, --txt          Write .TXT with the breakdown next to definition file.
      -x, --xlsx         Write .XLSX with the breakdown next to definition file.
      -i, --interactive  Enter interactive plot mode.
      -h, --help         Show this message and exit.

# ------------------------------------------------------------------------------
# That's all folks!
# ------------------------------------------------------------------------------
```

-----

## License

`pybudgetplot` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
