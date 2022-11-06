"""Unit-tests for the `pybudgetplot.utils.time_util` module."""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pandas import Timestamp

from pybudgetplot.utils.time_util import (
    Period,
    date_period,
    generate_date_stamps,
    is_normalized,
    parse_date_stamp,
    parse_time_stamp,
    stamp_to_str,
)


class IsNormalizedTests(TestCase):
    """Unit-tests for the `time_util.is_normalized` method."""

    def test_given_stamp_is_not_timestamp_instance_then_error(self):
        stamp = object()
        with self.assertRaises(TypeError) as ctx:
            is_normalized(stamp)  # noqa
        expected = (stamp, Timestamp, object)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)

    def test_given_stamp_is_timestamp_when_normalized_then_true(self):
        stamp = Timestamp(
            year=2022, month=1, day=2, hour=0, minute=0, microsecond=0
        )
        self.assertTrue(is_normalized(stamp))

    def test_given_stamp_is_timestamp_when_not_normalized_then_false(self):
        stamp = Timestamp(
            year=2022, month=1, day=2, hour=0, minute=0, microsecond=1
        )
        self.assertFalse(is_normalized(stamp))


class ParseTimeStampTests(TestCase):
    """Unit-tests for the `time_util.parse_time_stamp` method."""

    def test_given_none_then_value_error(self):
        value = None
        with self.assertRaises(ValueError) as ctx:
            parse_time_stamp(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_given_object_then_value_error(self):
        value = object()
        with self.assertRaises(ValueError) as ctx:
            parse_time_stamp(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_given_str_when_date_and_time_then_timestamp_returned(self):
        value = "2022-05-13 00:00:00"
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = parse_time_stamp(value)
        self.assertEqual(expected, actual)

    def test_given_str_when_date_only_then_timestamp_returned(self):
        value = "2022-05-13"
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = parse_time_stamp(value)
        self.assertEqual(expected, actual)

    def test_given_str_when_invalid_then_value_error(self):
        value = "bad value"
        with self.assertRaises(ValueError) as ctx:
            parse_time_stamp(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_given_timestamp_instance_then_same_object_returned(self):
        value = Timestamp(year=2022, month=5, day=13)
        result = parse_time_stamp(value)
        self.assertIs(value, result)


class ParseDateStampTests(TestCase):
    """Unit-tests for the `time_util.parse_date_stamp` method."""

    def test_given_none_then_value_error(self):
        value = None
        with self.assertRaises(ValueError) as ctx:
            parse_date_stamp(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_given_object_then_value_error(self):
        value = object()
        with self.assertRaises(ValueError) as ctx:
            parse_date_stamp(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_given_str_when_date_and_time_then_normalized_timestamp_returned(self):
        value = "2022-05-13 09:30:00"
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = parse_date_stamp(value)
        self.assertEqual(expected, actual)

    def test_given_str_when_date_only_then_normalized_timestamp_returned(self):
        value = "2022-05-13"
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = parse_date_stamp(value)
        self.assertEqual(expected, actual)

    def test_given_str_when_invalid_then_value_error(self):
        value = "bad value"
        with self.assertRaises(ValueError) as ctx:
            parse_date_stamp(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_given_timestamp_instance_then_normalized_timestamp_returned(self):
        value = Timestamp(year=2022, month=5, day=13, hour=9, minute=30)
        expected = Timestamp(year=2022, month=5, day=13).normalize()
        actual = parse_date_stamp(value)
        self.assertEqual(expected, actual)


class GenerateDateStampsTests(TestCase):
    """Unit-tests for the `time_util.generate_date_stamps` method."""

    def test_given_frequency_is_date_then_start_and_end_are_ignored(self):
        start = None
        end = None
        freq = "2022-05-01"
        expected = [Timestamp(year=2022, month=5, day=1).normalize()]
        actual = generate_date_stamps(freq, start, end)
        self.assertListEqual(expected, actual)

    def test_given_frequency_is_sentence_when_valid_then_correct(self):
        start = "2022-05-01"
        end = "2022-05-05"
        freq = "every day starting 2022-05-03 until 2022-05-05"
        expected = [
            Timestamp(year=2022, month=5, day=3).normalize(),
            Timestamp(year=2022, month=5, day=4).normalize(),
            Timestamp(year=2022, month=5, day=5).normalize(),
        ]
        actual = generate_date_stamps(freq, start, end)
        self.assertListEqual(expected, actual)

    def test_given_frequency_is_sentence_when_invalid_then_raises_error(self):
        start = "2022-05-01"
        end = "2022-05-05"
        freq = "sometimes"
        with self.assertRaises(ValueError) as ctx:
            generate_date_stamps(freq, start, end)
        expected = (freq,)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)


class StampToStrTests(TestCase):
    """Unit-tests for the `time_util.stamp_to_str` method."""

    def test_given_stamp_when_not_normalized_then_returns_iso_dateformat(self):
        stamp = Timestamp(
            year=2022, month=1, day=2, hour=3, minute=4, microsecond=5
        )
        expected = "2022-01-02 03:04:00.000005"
        actual = stamp_to_str(stamp)
        self.assertEqual(expected, actual)

    def test_given_stamp_when_normalized_then_returns_iso_dateformat(self):
        stamp = Timestamp(year=2022, month=1, day=2).normalize()
        expected = "2022-01-02"
        actual = stamp_to_str(stamp)
        self.assertEqual(expected, actual)


class PeriodTests(TestCase):
    """Unit-tests for the `Period` class."""

    def test_repr_with_non_normalized_timestamps(self):
        start = Timestamp(year=2022, month=1, day=10, hour=1)
        end = Timestamp(year=2022, month=2, day=20, hour=2, microsecond=2)
        period = Period(start, end)
        expected = (
            "Period("
            "start=Timestamp('2022-01-10 01:00:00'), "
            "end=Timestamp('2022-02-20 02:00:00.000002')"
            ")"
        )
        actual = repr(period)
        self.assertEqual(expected, actual)

    def test_repr_with_normalized_timestamps(self):
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

    def test_str_with_non_normalized_timestamps(self):
        start = Timestamp(year=2022, month=1, day=10, hour=1)
        end = Timestamp(year=2022, month=2, day=20, hour=2, microsecond=2)
        period = Period(start, end)
        expected = "['2022-01-10 01:00:00' - '2022-02-20 02:00:00.000002']"
        actual = str(period)
        self.assertEqual(expected, actual)

    def test_str_with_normalized_timestamps(self):
        start = Timestamp(year=2022, month=1, day=10).normalize()
        end = Timestamp(year=2022, month=2, day=20).normalize()
        period = Period(start, end)
        expected = "['2022-01-10' - '2022-02-20']"
        actual = str(period)
        self.assertEqual(expected, actual)

    def test_generate_dates_calls_generate_date_stamps(self):
        start = Timestamp(year=2022, month=1, day=10)
        end = Timestamp(year=2022, month=2, day=20)
        period = Period(start, end)
        expected_result = object()
        mock_generate_stamps = MagicMock(
            spec=generate_date_stamps,
            return_value=expected_result
        )
        method_name = "pybudgetplot.utils.time_util.generate_date_stamps"
        freq = object()
        with patch(method_name, new=mock_generate_stamps):
            actual_result = period.generate_dates(freq)  # noqa

        self.assertIs(expected_result, actual_result)
        mock_generate_stamps.assert_called_once_with(freq, start, end)


class DatePeriodTests(TestCase):
    """Unit-tests for the `time_util.date_period` method."""

    def test_given_valid_args_then_correct(self):
        start = "2022-01-13 22:45:00"
        end = "2022-02-24 00:23:00"
        expected = Period(
            Timestamp(year=2022, month=1, day=13).normalize(),
            Timestamp(year=2022, month=2, day=24).normalize(),
        )
        actual = date_period(start, end)
        self.assertEqual(expected, actual)
