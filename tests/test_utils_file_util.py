"""Unit-tests for the `pybudgetplot.utils.file_util` module."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pybudgetplot.utils.file_util import read_bytes, read_str, write_bytes, write_str


class ReadWriteBytesTests(TestCase):
    """Unit-tests for the `read_bytes` and `write_bytes` methods."""

    def test_given_file_when_exists_then_returns_bytes(self):
        expected_bytes = b"some bytes"
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            file = temp_dir_path.joinpath("child_dir").joinpath("some.file")
            self.assertFalse(file.exists())
            write_bytes(file, expected_bytes)
            self.assertTrue(file.exists())
            actual_bytes = read_bytes(file)
            file.unlink()
        self.assertEqual(expected_bytes, actual_bytes)

    def test_given_file_when_missing_then_raises_error(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            file = temp_dir_path.joinpath("missing.file")
            with self.assertRaises(FileNotFoundError):
                read_bytes(file)


class ReadWriteStrTests(TestCase):
    """Unit-tests for the `read_str` and `write_str` methods."""

    def test_given_file_when_exists_then_returns_bytes(self):
        expected_str = "some str"
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            file = temp_dir_path.joinpath("child_dir").joinpath("some.file")
            self.assertFalse(file.exists())
            write_str(file, expected_str)
            self.assertTrue(file.exists())
            actual_str = read_str(file)
            file.unlink()
        self.assertEqual(expected_str, actual_str)

    def test_given_file_when_missing_then_raises_error(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            file = temp_dir_path.joinpath("missing.file")
            with self.assertRaises(FileNotFoundError):
                read_str(file)
