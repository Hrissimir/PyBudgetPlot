# SPDX-FileCopyrightText: 2022-present Hrissimir <hrisimir.dakov@gmail.com>
#
# SPDX-License-Identifier: MIT
import sys

if __name__ == '__main__':
    from .cli import pybudgetplot

    sys.exit(pybudgetplot())  # pylint: disable=no-value-for-parameter
