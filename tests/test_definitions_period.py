"""Unit-tests for the `pybudgetplot.definitions.period` module."""

from unittest import TestCase

from pandas import Timestamp

from pybudgetplot.definitions.period import (
    PARSABLE_STAMP_TYPES,
    Period,
    format_timestamp,
    is_datestamp,
    new_period,
    parse_datestamp,
)


class IsDatestampTests(TestCase):
    """Unit-tests for the `period.is_datestamp` method."""

    def test_given_bad_param_type_then_raises_type_error(self):
        stamp = object()
        with self.assertRaises(TypeError) as ctx:
            is_datestamp(stamp)  # noqa
        expected = (stamp, Timestamp, object)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)

    def test_given_non_normalized_timestamp_then_returns_false(self):
        stamp = Timestamp(
            year=2022, month=1, day=2, hour=0, minute=0, microsecond=1
        )
        self.assertFalse(is_datestamp(stamp))

    def test_given_normalized_timestamp_then_returns_true(self):
        stamp = Timestamp(
            year=2022, month=1, day=2, hour=0, minute=0, microsecond=0
        )
        self.assertTrue(is_datestamp(stamp))


class ParseDatestampTests(TestCase):
    """Unit-tests for the `period.parse_datestamp` method."""

    def test_given_bad_param_type_then_raises_type_error(self):
        value = object()
        with self.assertRaises(TypeError) as ctx:
            parse_datestamp(value)
        expected_args = (value, PARSABLE_STAMP_TYPES, object)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_given_none_then_raises_type_error(self):
        value = None
        with self.assertRaises(TypeError) as ctx:
            parse_datestamp(value)
        expected_args = (value, PARSABLE_STAMP_TYPES, type(None))
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_given_str_when_not_parsable_then_raises_value_error(self):
        value = "bad value"
        with self.assertRaises(ValueError) as ctx:
            parse_datestamp(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_given_str_when_parsable_date_then_returns_timestamp(self):
        value = "2022-05-13"
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = parse_datestamp(value)
        self.assertEqual(expected, actual)

    def test_given_str_when_parsable_datetime_then_returns_timestamp(self):
        value = "2022-05-13 09:30:00"
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = parse_datestamp(value)
        self.assertEqual(expected, actual)

        value = "2022-05-13 00:00:00"
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = parse_datestamp(value)
        self.assertEqual(expected, actual)

    def test_given_timestamp_when_normalized_then_returns_same_object(self):
        value = Timestamp(year=2022, month=5, day=13)
        result = parse_datestamp(value)
        self.assertIs(value, result)

    def test_given_timestamp_when_non_normalized_then_returns_normalized_timestamp(self):
        value = Timestamp(year=2022, month=5, day=13, hour=10)
        expected = Timestamp(year=2022, month=5, day=13)
        actual = parse_datestamp(value)
        self.assertEqual(expected, actual)


class FormatTimestampTests(TestCase):
    """Unit-tests for the `period.format_timestamp` method."""

    def test_given_timestamp_when_non_normalized_then_returns_datetime_string(self):
        stamp = Timestamp(year=2022, month=1, day=2, hour=3, minute=4, microsecond=5)
        expected = "2022-01-02 03:04:00.000005"
        actual = format_timestamp(stamp)
        self.assertEqual(expected, actual)

    def test_given_timestamp_when_normalized_then_returns_iso_format_date_string(self):
        stamp = Timestamp(year=2022, month=1, day=2).normalize()
        expected = "2022-01-02"
        actual = format_timestamp(stamp)
        self.assertEqual(expected, actual)

    def test_given_bad_param_type_then_raises_type_error(self):
        stamp = object()
        with self.assertRaises(TypeError) as ctx:
            format_timestamp(stamp)  # noqa
        expected = (stamp, Timestamp, object)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)


class NewPeriodTests(TestCase):
    """Unit-tests for the `period.new_period` method."""

    def test_given_str_params_when_valid_datetime_values_then_returns_period(self):
        start = "2022-01-13 22:45:00"
        end = "2022-02-24 00:23:00"
        expected = Period(
            Timestamp(year=2022, month=1, day=13).normalize(),
            Timestamp(year=2022, month=2, day=24).normalize(),
        )
        actual = new_period(start, end)
        self.assertEqual(expected, actual)


class PeriodTests(TestCase):
    """Unit-tests for the `Period` class."""

    def test_as_dict(self):
        period = Period(
            Timestamp(year=2022, month=1, day=13).normalize(),
            Timestamp(year=2022, month=2, day=24).normalize(),
        )
        expected = {
            "start_date": "2022-01-13",
            "end_date": "2022-02-24",
        }
        actual = period.as_dict()
        self.assertDictEqual(expected, actual)

    def test_repr(self):
        start = Timestamp(year=2022, month=1, day=10).normalize()
        end = Timestamp(year=2022, month=2, day=20).normalize()
        period = Period(start, end)
        expected = (
            "Period("
            "start_date=Timestamp('2022-01-10 00:00:00'), "
            "end_date=Timestamp('2022-02-20 00:00:00')"
            ")"
        )
        actual = repr(period)
        self.assertEqual(expected, actual)

    def test_str(self):
        start = Timestamp(year=2022, month=1, day=10)
        end = Timestamp(year=2022, month=2, day=20, hour=2, microsecond=2)
        period = Period(start, end)
        expected = "['2022-01-10' - '2022-02-20 02:00:00.000002']"
        actual = str(period)
        self.assertEqual(expected, actual)

    def test_generate_dates_when_frequency_is_string_containing_date(self):
        period = new_period("2022-05-01", "2022-05-05")
        freq = "2022-05-01"
        expected = [Timestamp(year=2022, month=5, day=1).normalize()]
        actual = period.generate_dates(freq)
        self.assertListEqual(expected, actual)

    def test_generate_dates_when_frequency_is_string_containing_parsable_sentence(self):
        period = new_period("2022-05-01", "2022-05-05")
        freq = "every day starting 2022-05-03 until 2022-05-05"
        expected = [
            Timestamp(year=2022, month=5, day=3).normalize(),
            Timestamp(year=2022, month=5, day=4).normalize(),
            Timestamp(year=2022, month=5, day=5).normalize(),
        ]
        actual = period.generate_dates(freq)
        self.assertListEqual(expected, actual)

    def test_generate_dates_when_frequency_is_string_containing_non_parsable_sentence(self):
        period = new_period("2022-05-01", "2022-05-05")
        freq = "sometimes"
        with self.assertRaises(ValueError) as ctx:
            period.generate_dates(freq)
        expected = (freq,)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)
