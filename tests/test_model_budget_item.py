"""Unit-tests for the `pybudgetplot.model.budget_item` module."""
from unittest import TestCase

from pybudgetplot.model.budget_item import BudgetItem, new_item, parse_int, parse_string


class ParseStringTests(TestCase):
    """Unit-tests for the `budget_item.parse_string` method."""

    def test_given_value_when_non_empty_then_returns_stripped(self):
        value = " x \n \t y \r\t"
        expected = "x y"
        actual = parse_string(value)
        self.assertEqual(expected, actual)

    def test_given_value_when_non_str_instance_then_type_error(self):
        value = object()
        with self.assertRaises(TypeError) as ctx:
            parse_string(value)
        expected_args = (value, str, object)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)

    def test_given_value_when_whitespaces_only_then_value_error(self):
        value = "\n \r \t"
        with self.assertRaises(ValueError) as ctx:
            parse_string(value)
        expected_args = (value,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)


class ParseIntTests(TestCase):
    """Unit-tests for the `budget_item.parse_float` method."""

    def test_given_bad_type_then_raises_value_error(self):
        value = object()
        with self.assertRaises(ValueError) as ctx:
            parse_int(value)
        expected = (value,)
        actual = ctx.exception.args
        self.assertTupleEqual(expected, actual)

    def test_given_float_when_many_decimals_then_correct(self):
        value = 1.4949
        expected = 1
        actual = parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

        value = 1.4950
        expected = 1
        actual = parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

        value = 1.50
        expected = 2
        actual = parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

        value = 1.00
        expected = 1
        actual = parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

    def test_given_int_then_correct(self):
        value = 2
        expected = 2
        actual = parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

    def test_given_str_when_valid_float_then_correct(self):
        value = "23.4949"
        expected = 23
        actual = parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

        value = "23.4950"
        expected = 23
        actual = parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)

        value = "23.50"
        expected = 24
        actual = parse_int(value)
        self.assertIsInstance(actual, int)
        self.assertEqual(expected, actual)


class NewItemTests(TestCase):
    """Unit-tests for the `budget_item.new_item` method."""

    def test_given_valid_params_then_item_created(self):
        desc_param = " item \t \n desc \r"
        amount_param = "23.5"
        freq_param = "\n \t every day "
        expected = BudgetItem("item desc", 24, "every day")
        actual = new_item(desc_param, amount_param, freq_param)
        self.assertEqual(expected, actual)
