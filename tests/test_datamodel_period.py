"""Unit-tests for the `pybudgetplot.definitions.period` module."""
import re
from datetime import date, datetime
from unittest import TestCase

from pandas import Timestamp

from pybudgetplot.datamodel.period import Period, format_stamp, is_datestamp, parse_datestamp, parse_timestamp

REGEX_FLAGS = re.DOTALL | re.IGNORECASE


class IsDatestampTests(TestCase):
    """Unit-tests for the `is_datestamp` method."""

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


class ParseTimestampTests(TestCase):
    """Unit-tests for the `parse_timestamp` method."""

    def test_given_none_then_raises_value_error(self):
        value = None
        regex = r"can't parse None to Timestamp"
        pattern = re.compile(regex, REGEX_FLAGS)
        self.assertRaisesRegex(ValueError, pattern, parse_timestamp, value)

    def test_given_bad_type_then_raises_value_error(self):
        value = object()
        regex = r"error while parsing \<object object at .*\> to Timestamp"
        pattern = re.compile(regex, REGEX_FLAGS)
        self.assertRaisesRegex(ValueError, pattern, parse_timestamp, value)

    def test_given_date_instance_then_returns_timestamp(self):
        value = date(2022, 1, 23)
        expected = Timestamp(year=2022, month=1, day=23)
        actual = parse_timestamp(value)
        self.assertIsInstance(actual, Timestamp)
        self.assertEqual(expected, actual)

    def test_given_datetime_instance_then_returns_timestamp(self):
        value = datetime(2022, 11, 21, 1, 15, 20, 170705)
        expected = Timestamp(
            year=2022,
            month=11,
            day=21,
            hour=1,
            minute=15,
            second=20,
            microsecond=170705
        )
        actual = parse_timestamp(value)
        self.assertIsInstance(actual, Timestamp)
        self.assertEqual(expected, actual)

    def test_given_float_when_valid_timestamp_value_then_returns_utc_timestamp(self):
        value = 1668993320.170705
        expected = Timestamp(
            year=2022,
            month=11,
            day=21,
            hour=1,
            minute=15,
            second=20,
            microsecond=170705
        )
        actual = parse_timestamp(value)
        self.assertIsInstance(actual, Timestamp)
        self.assertEqual(expected, actual)

    def test_given_float_when_invalid_timestamp_value_then_raises_value_error(self):
        value = -1668993320.170705
        regex = r"error while parsing -1668993320.170705 to Timestamp"
        pattern = re.compile(regex, REGEX_FLAGS)
        self.assertRaisesRegex(ValueError, pattern, parse_timestamp, value)

    def test_given_int_when_valid_timestamp_value_then_returns_utc_timestamp(self):
        value = 1668993320
        expected = Timestamp(
            year=2022,
            month=11,
            day=21,
            hour=1,
            minute=15,
            second=20,
        )
        actual = parse_timestamp(value)
        self.assertIsInstance(actual, Timestamp)
        self.assertEqual(expected, actual)

    def test_given_int_when_invalid_timestamp_value_then_raises_value_error(self):
        value = -1668993320
        regex = r"error while parsing -1668993320 to Timestamp"
        pattern = re.compile(regex, REGEX_FLAGS)
        self.assertRaisesRegex(ValueError, pattern, parse_timestamp, value)

    def test_given_str_when_invalid_value_then_raises_value_error(self):
        value = "nope!"
        regex = r"error while parsing 'nope!' to Timestamp"
        pattern = re.compile(regex, REGEX_FLAGS)
        self.assertRaisesRegex(ValueError, pattern, parse_timestamp, value)

    def test_given_str_when_isodate_then_returns_timestamp(self):
        value = "2022-01-01"
        expected = Timestamp(year=2022, month=1, day=1)
        actual = parse_timestamp(value)
        self.assertIsInstance(actual, Timestamp)
        self.assertEqual(expected, actual)

    def test_given_str_when_isodatetime_then_returns_timestamp(self):
        value = "2022-11-21T01:15:20.170705"
        expected = Timestamp(
            year=2022,
            month=11,
            day=21,
            hour=1,
            minute=15,
            second=20,
            microsecond=170705
        )
        actual = parse_timestamp(value)
        self.assertIsInstance(actual, Timestamp)
        self.assertEqual(expected, actual)

    def test_given_timestamp_then_returns_same_object(self):
        value = Timestamp.now()
        self.assertIs(value, parse_timestamp(value))


class ParseDatestampTests(TestCase):
    """Unit-tests for the `parse_datestamp` method."""

    def test_given_non_normalized_timestamp_then_returns_datestamp(self):
        value = Timestamp(year=2022, month=5, day=13, hour=10)
        expected = Timestamp(year=2022, month=5, day=13)
        actual = parse_datestamp(value)
        self.assertEqual(expected, actual)

    def test_given_normalized_timestamp_then_returns_same_object(self):
        value = Timestamp(year=2022, month=5, day=13)
        result = parse_datestamp(value)
        self.assertIs(value, result)

    def test_given_str_when_parsable_date_then_returns_timestamp(self):
        value = "2022-05-13"
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = parse_datestamp(value)
        self.assertEqual(expected, actual)

    def test_given_str_when_parsable_datetime_then_returns_datestamp(self):
        value = "2022-05-13 09:30:00"
        expected = Timestamp(year=2022, month=5, day=13)
        actual = parse_datestamp(value)
        self.assertEqual(expected, actual)


class FormatStampTests(TestCase):
    """Unit-tests for the `format_stamp` method."""

    def test_given_bad_param_type_then_raises_type_error(self):
        stamp = object()
        with self.assertRaises(TypeError) as ctx:
            format_stamp(stamp)  # noqa
        expected = (stamp, Timestamp, object)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)

    def test_given_non_normalized_stamp_then_returns_iso_datetime(self):
        stamp = Timestamp(year=2022, month=1, day=2, hour=3, minute=4, microsecond=5)
        expected = "2022-01-02T03:04:00.000005"
        actual = format_stamp(stamp)
        self.assertEqual(expected, actual)

    def test_given_normalized_stamp_then_returns_iso_date(self):
        stamp = Timestamp(year=2022, month=1, day=2).normalize()
        expected = "2022-01-02"
        actual = format_stamp(stamp)
        self.assertEqual(expected, actual)


class PeriodTests(TestCase):
    """Unit-tests for the `Period` class."""

    def test_constructor(self):
        expected = Period(
            Timestamp(year=2022, month=1, day=13, hour=22, minute=45),
            Timestamp(year=2022, month=2, day=24, minute=23),
        )
        actual = Period("2022-01-13 22:45:00", "2022-02-24 00:23:00")
        self.assertEqual(expected, actual)

    def test_eq(self):
        current = Period("2022-01-13 22:45:00", "2022-02-24 00:23:00")
        other = object()
        self.assertFalse(current == other)

    def test_repr(self):
        start = Timestamp(year=2022, month=1, day=10).normalize()
        end = Timestamp(year=2022, month=2, day=20).normalize()
        period = Period(start, end)
        expected = (
            "Period("
            "start=Timestamp('2022-01-10 00:00:00'), "
            "end=Timestamp('2022-02-20 00:00:00')"
            ")"
        )
        actual = repr(period)
        self.assertEqual(expected, actual)

    def test_str(self):
        start = Timestamp(year=2022, month=1, day=10)
        end = Timestamp(year=2022, month=2, day=20, hour=2, microsecond=2)
        period = Period(start, end)
        expected = "['2022-01-10' - '2022-02-20T02:00:00.000002']"
        actual = str(period)
        self.assertEqual(expected, actual)

    def test_as_dict(self):
        period = Period(
            Timestamp(year=2022, month=1, day=13),
            Timestamp(year=2022, month=2, day=24),
        )
        expected = {"start": "2022-01-13", "end": "2022-02-24"}
        actual = period.as_dict()
        self.assertDictEqual(expected, actual)

    def test_generate_datestamps_from_bad_param_type(self):
        period = Period("2022-05-01", "2022-05-05")
        freq = object()
        with self.assertRaises(TypeError) as ctx:
            period.generate_datestamps(freq)  # noqa
        expected = (freq, str, object)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)

    def test_generate_datestamps_from_isoformat_date(self):
        period = Period("2022-05-01", "2022-05-05")
        freq = "2022-05-01"
        expected = [Timestamp(year=2022, month=5, day=1)]
        actual = period.generate_datestamps(freq)
        self.assertListEqual(expected, actual)

    def test_generate_datestamps_from_non_parsable_sentence(self):
        period = Period("2022-05-01", "2022-05-05")
        freq = "sometimes"
        with self.assertRaises(ValueError) as ctx:
            period.generate_datestamps(freq)
        expected = (freq,)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)

    def test_generate_datestamps_from_parsable_sentence(self):
        period = Period("2022-05-01", "2022-05-05")
        freq = "every day starting 2022-05-03 until 2022-05-05"
        expected = [
            Timestamp(year=2022, month=5, day=3),
            Timestamp(year=2022, month=5, day=4),
            Timestamp(year=2022, month=5, day=5),
        ]
        actual = period.generate_datestamps(freq)
        self.assertListEqual(expected, actual)
