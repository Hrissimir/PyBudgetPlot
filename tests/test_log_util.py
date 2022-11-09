"""Unit-tests for the ``pybudgetplot.utils.log_util`` module."""
import io
import logging
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from pybudgetplot.utils.log_util import (
    LOG_DATE_FORMAT_DEBUG,
    LOG_DATE_FORMAT_INFO,
    LOG_FORMAT_DEBUG,
    LOG_FORMAT_INFO,
    LOG_FORMATTER_CONVERTER_DEBUG,
    LOG_FORMATTER_CONVERTER_INFO,
    add_file_handler,
    create_file_handler,
    create_formatter,
    get_log_date_format,
    get_log_format,
    get_log_formatter_converter,
    init_logging,
    remove_handlers,
    to_level,
)


class ToLevelTestCase(TestCase):
    """Unit-tests for the ``log_util.to_level`` method."""

    def test_given_level_name_and_when_upper_case_when_valid_then_correct(self):
        self.assertEqual(logging.DEBUG, to_level("DEBUG"))

    def test_given_level_name_and_lower_case_when_valid_then_correct(self):
        self.assertEqual(logging.INFO, to_level("info"))

    def test_given_level_name_and_mixed_case_when_valid_then_correct(self):
        self.assertEqual(logging.WARNING, to_level("wArN"))

    def test_given_level_name_and_whitespaces_when_valid_then_correct(self):
        self.assertEqual(logging.NOTSET, to_level(" No t Set "))

    def test_given_level_value_when_valid_then_correct(self):
        self.assertEqual(40, to_level(logging.ERROR))

    def test_given_level_name_when_invalid_then_none(self):
        self.assertIsNone(to_level("what"))

    def test_given_level_value_when_invalid_then_none(self):
        self.assertIsNone(to_level(-20))

    def test_given_empty_str_then_none(self):
        self.assertIsNone(to_level(""))

    def test_given_none_name_then_none(self):
        self.assertIsNone(to_level("nOne"))

    def test_given_none_obj_then_none(self):
        self.assertIsNone(to_level(None))


class GetLogFormatTestCase(TestCase):
    """Unit-tests for the ``log_util.get_log_format`` method."""

    def test_given_level_when_debug_name_then_returns_debug_format(self):
        arg = "DEBUG"
        expected = LOG_FORMAT_DEBUG
        actual = get_log_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_debug_value_then_returns_debug_format(self):
        arg = logging.DEBUG
        expected = LOG_FORMAT_DEBUG
        actual = get_log_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_empty_str_then_returns_debug_format(self):
        arg = ""
        expected = LOG_FORMAT_DEBUG
        actual = get_log_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_info_name_then_returns_info_format(self):
        arg = " i n f O "
        expected = LOG_FORMAT_INFO
        actual = get_log_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_info_value_then_returns_info_format(self):
        arg = logging.INFO
        expected = LOG_FORMAT_INFO
        actual = get_log_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_none_then_returns_debug_format(self):
        arg = None
        expected = LOG_FORMAT_DEBUG
        actual = get_log_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_not_info_or_debug_then_returns_debug_format(self):
        arg = " warn "
        expected = LOG_FORMAT_DEBUG
        actual = get_log_format(arg)
        self.assertEqual(expected, actual)


class GetLogDateFormatTestCase(TestCase):
    """Unit-tests for the ``log_util.get_log_date_format`` method."""

    def test_given_level_when_debug_name_then_returns_debug_format(self):
        arg = "DEBUG"
        expected = LOG_DATE_FORMAT_DEBUG
        actual = get_log_date_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_debug_value_then_returns_debug_format(self):
        arg = logging.DEBUG
        expected = LOG_DATE_FORMAT_DEBUG
        actual = get_log_date_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_empty_str_then_returns_debug_format(self):
        arg = ""
        expected = LOG_DATE_FORMAT_DEBUG
        actual = get_log_date_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_info_name_then_returns_info_format(self):
        arg = " i n f O "
        expected = LOG_DATE_FORMAT_INFO
        actual = get_log_date_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_info_value_then_returns_info_format(self):
        arg = logging.INFO
        expected = LOG_DATE_FORMAT_INFO
        actual = get_log_date_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_none_then_returns_debug_format(self):
        arg = None
        expected = LOG_DATE_FORMAT_DEBUG
        actual = get_log_date_format(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_not_info_or_debug_then_returns_debug_format(self):
        arg = " warn "
        expected = LOG_DATE_FORMAT_DEBUG
        actual = get_log_date_format(arg)
        self.assertEqual(expected, actual)


class GetLogFormatterConverterTestCase(TestCase):
    """Unit-tests for the ``log_util.get_log_formatter_converter`` method."""

    def test_given_level_when_debug_name_then_returns_debug_converter(self):
        arg = "DEBUG"
        expected = LOG_FORMATTER_CONVERTER_DEBUG
        actual = get_log_formatter_converter(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_debug_value_then_returns_debug_converter(self):
        arg = logging.DEBUG
        expected = LOG_FORMATTER_CONVERTER_DEBUG
        actual = get_log_formatter_converter(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_empty_str_then_returns_debug_converter(self):
        arg = ""
        expected = LOG_FORMATTER_CONVERTER_DEBUG
        actual = get_log_formatter_converter(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_info_name_then_returns_info_converter(self):
        arg = " i n f O "
        expected = LOG_FORMATTER_CONVERTER_INFO
        actual = get_log_formatter_converter(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_info_value_then_returns_info_converter(self):
        arg = logging.INFO
        expected = LOG_FORMATTER_CONVERTER_INFO
        actual = get_log_formatter_converter(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_none_then_returns_debug_converter(self):
        arg = None
        expected = LOG_FORMATTER_CONVERTER_DEBUG
        actual = get_log_formatter_converter(arg)
        self.assertEqual(expected, actual)

    def test_given_level_when_not_info_or_debug_then_returns_debug_converter(self):
        arg = " warn "
        expected = LOG_FORMATTER_CONVERTER_DEBUG
        actual = get_log_formatter_converter(arg)
        self.assertEqual(expected, actual)


class CreateFormatterTestCase(TestCase):
    """Unit-tests for the ``log_util.create_formatter`` method."""

    def test_given_level_name_when_then_created(self):
        level = "debug"

        fmt = LOG_FORMAT_DEBUG
        datefmt = LOG_DATE_FORMAT_DEBUG
        converter = LOG_FORMATTER_CONVERTER_DEBUG

        module = "pybudgetplot.utils.log_util"
        with patch(f"{module}.get_log_format", return_value=fmt) as get_fmt, patch(
            f"{module}.get_log_date_format", return_value=datefmt
        ) as get_datefmt, patch(
            f"{module}.get_log_formatter_converter", return_value=converter
        ) as get_conv:
            formatter = create_formatter(level)
        self.assertIsInstance(formatter, logging.Formatter)
        get_fmt.assert_called_once_with(level)
        get_datefmt.assert_called_once_with(level)
        get_conv.assert_called_once_with(level)
        self.assertIs(converter, formatter.converter)


class CreateFileHandlerTestCase(TestCase):
    """Unit-tests for the ``log_util.create_file_handler`` method."""

    def test_given_file_parent_dir_exists_then_handler_created(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir).absolute().resolve(strict=False)

            existing_dir = temp_dir_path / "existing_dir"
            existing_dir = existing_dir.absolute().resolve(strict=False)

            self.assertFalse(existing_dir.exists())
            existing_dir.mkdir()
            self.assertTrue(existing_dir.exists())

            file_path = existing_dir / "out.log"
            file_path = file_path.absolute().resolve(strict=False)
            self.assertFalse(file_path.exists())

            file = str(file_path)
            handler = create_file_handler(file)
            self.assertIsInstance(handler, logging.FileHandler)
            handler.flush()
            handler.close()

            self.assertTrue(file_path.exists())
            self.assertEqual(file, handler.baseFilename)

    def test_given_file_parent_dir_not_exists_then_parent_dir_created(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir).absolute().resolve(strict=False)

            file_dir = temp_dir_path / "missing_dir"
            file_dir = file_dir.absolute().resolve(strict=False)
            self.assertFalse(file_dir.exists())

            file_path = file_dir / "out.log"
            file_path = file_path.absolute().resolve(strict=False)
            self.assertFalse(file_path.exists())

            file = str(file_path)

            handler = create_file_handler(file)
            self.assertIsInstance(handler, logging.FileHandler)
            handler.flush()
            handler.close()

            self.assertTrue(file_dir.exists())
            self.assertTrue(file_path.exists())

            expected_filename = file
            actual_filename = handler.baseFilename
            self.assertEqual(expected_filename, actual_filename)

    def test_given_file_parent_dir_is_file_then_error_raised(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            file_dir = temp_dir_path / "missing_dir"
            file_dir = file_dir.absolute().resolve(strict=False)
            self.assertFalse(file_dir.exists())

            file_dir.write_text("some text to create the file", encoding="utf8")
            self.assertTrue(file_dir.exists())

            file_path = file_dir / "out.log"
            file_path = file_path.absolute().resolve(strict=False)
            self.assertFalse(file_path.exists())

            file = str(file_path)
            with self.assertRaises(NotADirectoryError) as ctx:
                create_file_handler(file)

            self.assertFalse(file_path.exists())

        expected_args = (file_dir,)
        actual_args = ctx.exception.args
        self.assertTupleEqual(expected_args, actual_args)


class RemoveHandlersTestCase(TestCase):
    """Unit-tests for the ``log_util.remove_handlers`` method."""

    def test_given_logger_with_no_handlers_then_no_handlers_removed(self):
        mock_logger = MagicMock()
        mock_logger.handlers = []

        remove_handlers(mock_logger)

        # verify removeHandler not called at all
        expected_calls = []
        actual_calls = mock_logger.removeHandler.mock_calls
        self.assertListEqual(expected_calls, actual_calls)

    def test_given_logger_with_some_handlers_then_handlers_removed(self):
        mock_logger = MagicMock()
        handler_1 = MagicMock(spec=logging.Handler)
        handler_2 = MagicMock(spec=logging.Handler)
        mock_logger.handlers = [handler_1, handler_2]

        remove_handlers(mock_logger)

        # verify removeHandler called with each handler
        expected_remove_calls = [call(handler_1), call(handler_2)]
        actual_remove_calls = mock_logger.removeHandler.mock_calls
        self.assertListEqual(expected_remove_calls, actual_remove_calls)

        # verify all handlers were flushed and closed
        handler_1.flush.assert_called_once()
        handler_1.close.assert_called_once()
        handler_2.flush.assert_called_once()
        handler_2.close.assert_called_once()


class AddFileHandlerTestCase(TestCase):
    """Unit-tests for the ``log_util.add_file_handler`` method."""

    def test_given_valid_args_then_handler_added(self):
        logger = logging.getLogger(
            "AddFileHandlerTestCase.test_given_valid_args_then_handler_added"
        )
        remove_handlers(logger)
        self.assertEqual(0, len(logger.handlers))

        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir).absolute().resolve(strict=False)
            file = temp_dir_path / "out.log"
            file = file.absolute().resolve(strict=False)
            level = "info"

            handler = add_file_handler(logger, file, level)
            self.assertIsInstance(handler, logging.FileHandler)
            self.addCleanup(handler.flush)
            self.addCleanup(handler.close)

            expected_filename = str(file)
            actual_filename = handler.baseFilename
            self.assertEqual(expected_filename, actual_filename)

            expected_level = logging.INFO
            actual_level = handler.level
            self.assertEqual(expected_level, actual_level)

            handler.flush()
            handler.close()


class InitLoggingTestCase(TestCase):
    """Unit-tests for the ``log_util.init_logging`` method."""

    def test_given_level_debug_when_stream_arg_and_file_arg_then_initialized(self):
        buffer = io.BytesIO()
        stream = io.TextIOWrapper(buffer, "utf-8", "surrogateescape", "\n")
        with TemporaryDirectory() as temp_dir, patch(
            "logging.Formatter"
        ) as mock_formatter_cls, patch(
            "logging.basicConfig"
        ) as mock_config_method, patch(
            "pybudgetplot.utils.log_util.add_file_handler"
        ) as mock_add_file_handler:
            temp_dir_path = Path(temp_dir)
            file = temp_dir_path.joinpath("out.log")

            init_logging("debug", stream=stream, file=file)

            actual_converter = mock_formatter_cls.converter

        # assert ``logging.Formatter.converter`` was updated correctly
        self.assertEqual(LOG_FORMATTER_CONVERTER_DEBUG, actual_converter)

        # assert ``logging.basicConfig`` called once with correct params
        expected_config_calls = [
            call(
                level=logging.DEBUG,
                format=LOG_FORMAT_DEBUG,
                datefmt=LOG_DATE_FORMAT_DEBUG,
                stream=stream,
            ),
        ]
        actual_config_calls = mock_config_method.mock_calls
        self.assertListEqual(expected_config_calls, actual_config_calls)

        # assert ``log_util.add_file_handler`` called once with correct params
        expected_add_handler_calls = [call(logging.getLogger(), file, logging.DEBUG)]
        actual_add_handler_calls = mock_add_file_handler.mock_calls
        self.assertListEqual(expected_add_handler_calls, actual_add_handler_calls)

    def test_given_level_info_when_stream_passed_then_initialized(self):
        buffer = io.BytesIO()
        stream = io.TextIOWrapper(buffer, "utf-8", "surrogateescape", "\n")
        with patch("logging.Formatter") as mock_formatter_cls, patch(
            "logging.basicConfig"
        ) as mock_config_method, patch(
            "pybudgetplot.utils.log_util.add_file_handler"
        ) as mock_add_file_handler:
            init_logging("info", stream=stream)

            actual_converter = mock_formatter_cls.converter

        # assert ``logging.Formatter.converter`` was updated correctly
        self.assertEqual(LOG_FORMATTER_CONVERTER_INFO, actual_converter)

        # assert ``logging.basicConfig`` called once with correct params
        expected_config_calls = [
            call(
                level=logging.INFO,
                format=LOG_FORMAT_INFO,
                datefmt=LOG_DATE_FORMAT_INFO,
                stream=stream,
            )
        ]
        actual_config_calls = mock_config_method.mock_calls
        self.assertListEqual(expected_config_calls, actual_config_calls)

        # assert ``log_util.add_file_handler`` not called at all
        mock_add_file_handler.assert_not_called()

    def test_given_level_none_when_stream_not_passed_and_file_not_passed_then_initialized(
        self,
    ):
        with patch("logging.Formatter") as mock_formatter_cls, patch(
            "logging.basicConfig"
        ) as mock_config_method, patch(
            "pybudgetplot.utils.log_util.add_file_handler"
        ) as mock_add_file_handler:
            init_logging(None)

            actual_converter = mock_formatter_cls.converter

        # assert ``logging.Formatter.converter`` was updated correctly
        self.assertEqual(LOG_FORMATTER_CONVERTER_DEBUG, actual_converter)

        # assert ``logging.basicConfig`` called once with correct params
        expected_config_calls = [
            call(
                level=None,
                format=LOG_FORMAT_DEBUG,
                datefmt=LOG_DATE_FORMAT_DEBUG,
                stream=sys.stdout,
            )
        ]
        actual_config_calls = mock_config_method.mock_calls
        self.assertListEqual(expected_config_calls, actual_config_calls)

        # assert ``log_util.add_file_handler`` not called at all
        mock_add_file_handler.assert_not_called()
