"""Unit-tests for all classes and methods in `pybudgetplot.datamodel` module."""

from textwrap import dedent
from unittest import TestCase

from pandas import DataFrame, Timestamp

from pybudgetplot.datamodel import BudgetDefinition, BudgetItem, DatePeriod

# Period data
START_DATESTAMP = Timestamp(year=2021, month=12, day=31).normalize()
END_DATESTAMP = Timestamp(year=2022, month=1, day=5).normalize()
PERIOD = DatePeriod(START_DATESTAMP, END_DATESTAMP)

# Item data
ITEM_CASH = BudgetItem("cash", 200, "2021-12-31")

ITEM_FOOD = BudgetItem("food", -5, "every day starting 2022-01-01")

ITEM_COMMUTE = BudgetItem("commute", -1, "every day starting 2022-01-02 until 2022-01-04")

# Budget data
BUDGET = BudgetDefinition(START_DATESTAMP, END_DATESTAMP)
BUDGET.items.extend([ITEM_CASH, ITEM_FOOD, ITEM_COMMUTE])

BUDGET_YAML_STR = dedent(
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

BUDGET_YAML_BYTES = BUDGET_YAML_STR.encode(
    encoding="utf-8",
    errors="surrogateescape"
)

BUDGET_CSV_STR = dedent(
    """\
    date,cash,food,commute,daily_total,cumulative_total
    2021-12-31,200,0,0,200,200
    2022-01-01,0,-5,0,-5,195
    2022-01-02,0,-5,-1,-6,189
    2022-01-03,0,-5,-1,-6,183
    2022-01-04,0,-5,-1,-6,177
    2022-01-05,0,-5,0,-5,172
    """
)

BUDGET_CSV_BYTES = BUDGET_CSV_STR.encode(
    encoding="utf-8",
    errors="surrogateescape"
)


class DatePeriodTests(TestCase):
    """Unit-tests for the `DatePeriod` class."""

    def test_constructor_converts_params_to_datestamps(self):
        start = "2022-01-13 22:45:00"
        end = "2022-02-24 00:23:00"
        expected = DatePeriod(
            Timestamp(year=2022, month=1, day=13).normalize(),
            Timestamp(year=2022, month=2, day=24).normalize(),
        )
        actual = DatePeriod(start, end)
        self.assertEqual(expected, actual)

    def test_format_timestamp_with_non_normalized_timestamp(self):
        stamp = Timestamp(
            year=2022, month=1, day=2, hour=3, minute=4, microsecond=5
        )
        expected = "2022-01-02 03:04:00.000005"
        actual = DatePeriod.format_timestamp(stamp)
        self.assertEqual(expected, actual)

    def test_format_timestamp_with_normalized_timestamp(self):
        stamp = Timestamp(year=2022, month=1, day=2).normalize()
        expected = "2022-01-02"
        actual = DatePeriod.format_timestamp(stamp)
        self.assertEqual(expected, actual)

    def test_generate_dates_with_frequency_date_string(self):
        period = DatePeriod("2022-05-01", "2022-05-05")
        freq = "2022-05-01"
        expected = [Timestamp(year=2022, month=5, day=1).normalize()]
        actual = period.generate_dates(freq)
        self.assertListEqual(expected, actual)

    def test_generate_dates_with_frequency_invalid_sentence(self):
        period = DatePeriod("2022-05-01", "2022-05-05")
        freq = "sometimes"
        with self.assertRaises(ValueError) as ctx:
            period.generate_dates(freq)
        expected = (freq,)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)

    def test_generate_dates_with_frequency_valid_sentence(self):
        period = DatePeriod("2022-05-01", "2022-05-05")
        freq = "every day starting 2022-05-03 until 2022-05-05"
        expected = [
            Timestamp(year=2022, month=5, day=3).normalize(),
            Timestamp(year=2022, month=5, day=4).normalize(),
            Timestamp(year=2022, month=5, day=5).normalize(),
        ]
        actual = period.generate_dates(freq)
        self.assertListEqual(expected, actual)

    def test_is_datestamp_with_bad_type(self):
        stamp = object()
        with self.assertRaises(TypeError) as ctx:
            DatePeriod.is_datestamp(stamp)  # noqa
        expected = (stamp, Timestamp, object)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)

    def test_is_datestamp_with_non_normalized_timestamp(self):
        stamp = Timestamp(
            year=2022, month=1, day=2, hour=0, minute=0, microsecond=1
        )
        self.assertFalse(DatePeriod.is_datestamp(stamp))

    def test_is_datestamp_with_normalized_timestamp(self):
        stamp = Timestamp(
            year=2022, month=1, day=2, hour=0, minute=0, microsecond=0
        )
        self.assertTrue(DatePeriod.is_datestamp(stamp))

    def test_parse_datestamp_with_bad_string(self):
        value = "bad value"
        with self.assertRaises(ValueError) as ctx:
            DatePeriod.parse_datestamp(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_parse_datestamp_with_bad_type(self):
        value = object()
        with self.assertRaises(ValueError) as ctx:
            DatePeriod.parse_datestamp(value)  # noqa
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_parse_datestamp_with_date_string(self):
        value = "2022-05-13"
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = DatePeriod.parse_datestamp(value)
        self.assertEqual(expected, actual)

    def test_parse_datestamp_with_non_normalized_timestamp_string(self):
        value = "2022-05-13 09:30:00"
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = DatePeriod.parse_datestamp(value)
        self.assertEqual(expected, actual)

    def test_parse_datestamp_with_none(self):
        value = None
        with self.assertRaises(ValueError) as ctx:
            DatePeriod.parse_datestamp(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_parse_datestamp_with_normalized_datetime_string(self):
        value = "2022-05-13 00:00:00"
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = DatePeriod.parse_datestamp(value)
        self.assertEqual(expected, actual)

    def test_parse_datestamp_with_normalized_timestamp(self):
        value = Timestamp(year=2022, month=5, day=13)
        result = DatePeriod.parse_datestamp(value)
        self.assertIs(value, result)

    def test_repr(self):
        start = Timestamp(year=2022, month=1, day=10).normalize()
        end = Timestamp(year=2022, month=2, day=20).normalize()
        period = DatePeriod(start, end)
        expected = (
            "DatePeriod("
            "start=Timestamp('2022-01-10 00:00:00'), "
            "end=Timestamp('2022-02-20 00:00:00')"
            ")"
        )
        actual = repr(period)
        self.assertEqual(expected, actual)

    def test_str(self):
        start = Timestamp(year=2022, month=1, day=10, hour=1)
        end = Timestamp(year=2022, month=2, day=20, hour=2, microsecond=2)
        period = DatePeriod(start, end)
        expected = "['2022-01-10' - '2022-02-20']"
        actual = str(period)
        self.assertEqual(expected, actual)


class BudgetItemTests(TestCase):
    """Unit-tests for the `BudgetItem` class."""

    def test_constructor(self):
        desc_param = " item \t \n desc \r"
        amount_param = "23.5"
        freq_param = "\n \t every day "
        expected = BudgetItem("item desc", 24, "every day")
        actual = BudgetItem(desc_param, amount_param, freq_param)
        self.assertEqual(expected, actual)

    def test_normalize_string_when_non_empty_result(self):
        value = " x \n \t y \r\t"
        expected = "x y"
        actual = BudgetItem.normalize_string(value)
        self.assertEqual(expected, actual)

    def test_normalize_string_when_empty_result(self):
        value = "\n \r \t"
        with self.assertRaises(ValueError) as ctx:
            BudgetItem.normalize_string(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_parse_int_with_bad_type(self):
        value = object()
        with self.assertRaises(ValueError) as ctx:
            BudgetItem.parse_int(value)
        expected = (value,)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)

    def test_parse_int_with_float(self):
        value = 1.4949
        expected = 1
        actual = BudgetItem.parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

        value = 1.4950
        expected = 1
        actual = BudgetItem.parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

        value = 1.50
        expected = 2
        actual = BudgetItem.parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

        value = 1.00
        expected = 1
        actual = BudgetItem.parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

    def test_parse_int_with_str(self):
        value = "23.4949"
        expected = 23
        actual = BudgetItem.parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

        value = "23.4950"
        expected = 23
        actual = BudgetItem.parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

        value = "23.50"
        expected = 24
        actual = BudgetItem.parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)


class BudgetDefinitionTests(TestCase):
    """Unit-tests for the `BudgetDefinition` class."""

    def test_constructor(self):
        start_param = "2022-01-01"
        end_param = "2022-01-31"
        budget = BudgetDefinition(start_param, end_param)
        self.assertIsInstance(budget, BudgetDefinition)

        expected_period = DatePeriod(
            Timestamp(year=2022, month=1, day=1).normalize(),
            Timestamp(year=2022, month=1, day=31).normalize(),
        )
        actual_period = budget.period
        self.assertEqual(expected_period, actual_period)

        self.assertIsInstance(budget.items, list)
        self.assertEqual(0, len(budget.items))

    def test_add_item(self):
        budget = BudgetDefinition("2022-01-01", "2022-01-31")
        desc = " item \t desc\n"
        amount = "23.50"
        freq = "every \t \n day "
        budget.add_item(desc, amount, freq)
        expected_item = BudgetItem("item desc", 24, "every day")
        self.assertIn(expected_item, budget.items)
        self.assertEqual(1, len(budget.items))

    def test_as_yaml(self):
        self.assertEqual(BUDGET_YAML_STR, BUDGET.as_yaml())

    def test_from_yaml(self):
        self.assertEqual(BUDGET, BudgetDefinition.from_yaml(BUDGET_YAML_STR))

    def test_calculate_breakdown(self):
        breakdown = BUDGET.calculate_breakdown()
        self.assertIsInstance(breakdown, DataFrame)

        expected = dedent(
            # pylint: disable=trailing-whitespace
            """\
                         cash  food  commute  daily_total  cumulative_total
            date
            2021-12-31  200.0   0.0      0.0        200.0             200.0
            2022-01-01    0.0  -5.0      0.0         -5.0             195.0
            2022-01-02    0.0  -5.0     -1.0         -6.0             189.0
            2022-01-03    0.0  -5.0     -1.0         -6.0             183.0
            2022-01-04    0.0  -5.0     -1.0         -6.0             177.0
            2022-01-05    0.0  -5.0      0.0         -5.0             172.0"""
        )
        actual = "\n".join([
            line.rstrip()
            for line
            in str(breakdown).splitlines(False)
        ])
        self.assertEqual(expected, actual)

    def test_to_csv(self):
        self.assertEqual(BUDGET_CSV_BYTES, BUDGET.to_csv())

    def test_to_xlsx(self):
        xlsx_bytes = BUDGET.to_xlsx()
        min_bytes_count = 6990
        actual_bytes_count = len(xlsx_bytes)
        self.assertGreaterEqual(actual_bytes_count, min_bytes_count)
