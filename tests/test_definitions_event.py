"""Unit-tests for the `pybudgetplot.definitions.event` module."""
import logging
from unittest import TestCase

from pybudgetplot.definitions.event import Event, normalize_string, parse_amount

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class NormalizeStringTests(TestCase):
    """Unit-tests for the `event.normalize_string` method."""

    def test_given_bad_type_param_then_raises_type_error(self):
        value = object()
        with self.assertRaises(TypeError) as ctx:
            normalize_string(value)
        expected = (value, str, object)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)

    def test_given_string_when_non_whitespace_only_then_returns_normalized(self):
        value = " x \n \t y \r\t"
        expected = "x y"
        actual = normalize_string(value)
        self.assertEqual(expected, actual)

    def test_given_string_when_whitespace_only_then_raises_value_error(self):
        value = "\n \r \t"
        with self.assertRaises(ValueError) as ctx:
            normalize_string(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)


class ParseAmountTests(TestCase):
    """Unit-tests for the `event.parse_amount` method."""

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

    def test_new(self):
        desc_param = " evt \t \n desc \r"
        amount_param = "23.5"
        freq_param = "\n \t every day "
        expected = Event("evt desc", 23.5, "every day")
        actual = Event.new(desc_param, amount_param, freq_param)
        self.assertEqual(expected, actual)

    def test_as_dict(self):
        event = Event("evt desc", 23.5, "every day")
        expected = {
            "description": "evt desc",
            "amount": "23.50",
            "frequency": "every day"
        }
        actual = event.as_dict()
        self.assertDictEqual(expected, actual)
