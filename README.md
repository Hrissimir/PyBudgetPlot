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

-----

## Installation

The project can be installed from PyPI using the following command:

```console
pip install pybudgetplot
```

-----

## Usage

### 1. *Initialize* a sample *'budget-definition'* file.

```shell
budget-init  # creates a 'budget.yaml' file in the current work-dir

budget-init -h  # shows all command options and usage instructions
```

### 2. *Update* the sample *'budget-definition'* file.

The file contains several examples of how a *'budget-event'* can be defined.

Use them to define your own list of *'budget-events'* that you want to plot.

### 3. *Calculate* the budget *'daily'* and *'cumulative'* totals.

During the calculation:

* A list of all dates for the period is generated
* The *frequency* of each *budget-event* is parsed to list of dates
* The *event-amount* is added to each date that falls inside the period
* The *daily-total* value for each day is calculated by summing-up all amounts
* The *cumulative-total* value for each date is calculated based on previous day

```shell
budget-calc  # reads the budget.yaml file and generates a budget.xlsx file

budget-calc -h  # shows all command options and usage instructions
```

### 4. *Plot* a visualization of the calculated *daily* and *cumulative* totals.

```shell
budget-plot  # reads the budget.yaml file and generates a budget.png file

budget-plot -h  # shows all command options and usage instructions
```

-----

## License

`pybudgetplot` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
