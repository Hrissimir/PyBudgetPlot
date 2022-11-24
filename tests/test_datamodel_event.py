"""Unit-tests for the `pybudgetplot.definitions.event` module."""
import datetime
from unittest import TestCase

from pybudgetplot.datamodel.event import Event, parse_amount, parse_string


class ParseStringTests(TestCase):
    """Unit-tests for the `parse_string` method."""

    def test_given_object_then_returns_object_to_string(self):
        value = object()
        expected = str(value)
        actual = parse_string(value)
        self.assertEqual(expected, actual)

    def test_given_string_when_non_whitespace_only_then_returns_normalized(self):
        value = " x \n \t y \r\t"
        expected = "x y"
        actual = parse_string(value)
        self.assertEqual(expected, actual)

    def test_given_string_when_whitespace_only_then_raises_value_error(self):
        value = "\n \r \t"
        with self.assertRaises(ValueError) as ctx:
            parse_string(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)


class ParseAmountTests(TestCase):
    """Unit-tests for the `parse_amount` method."""

    def test_given_bad_type_param_then_raises_type_error(self):
        value = object()
        with self.assertRaises(ValueError) as ctx:
            parse_amount(value)
        expected = (value,)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)

    def test_given_float_then_returns_same_float(self):
        value = 1.4949
        expected = 1.4949
        actual = parse_amount(value)
        self.assertEqual(expected, actual)

    def test_given_int_then_returns_float(self):
        value = 2
        expected = float(2)
        actual = parse_amount(value)
        self.assertIsInstance(actual, float)
        self.assertEqual(expected, actual)

    def test_given_str_then_returns_float(self):
        value = "-23.4949"
        expected = -23.4949
        actual = parse_amount(value)
        self.assertEqual(expected, actual)


class EventTests(TestCase):
    """Unit-tests for the `Event` class."""

    def test_constructor(self):
        desc_param = " evt \t \n desc \r"
        amount_param = "23.5"
        freq_param = "\n \t every day "
        expected = Event("evt desc", 23.5, "every day")
        actual = Event(desc_param, amount_param, freq_param)
        self.assertEqual(expected, actual)

        freq_param = datetime.date.fromisoformat("2022-11-13")
        expected.frequency = freq_param.isoformat()
        actual = Event(desc_param, amount_param, freq_param)
        self.assertEqual(expected, actual)

    def test_repr(self):
        event = Event("evt desc", 23.5, "every day")
        expected = "Event(description='evt desc', amount=23.5, frequency='every day')"
        actual = repr(event)
        self.assertEqual(expected, actual)

    def test_eq(self):
        current = Event("evt desc", 23.5, "every day")
        other = object()
        self.assertFalse(current == other)
