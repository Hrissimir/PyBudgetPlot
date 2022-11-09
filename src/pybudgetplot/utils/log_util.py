"""Helper module for initializing the logging framework."""
import atexit
import logging
import re
import sys
import time
from os import PathLike
from pathlib import Path
from typing import Any, Callable, NoReturn, Optional, TextIO, Union

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

NAME_TO_LEVEL = {
    "CRITICAL": CRITICAL,
    "FATAL": FATAL,
    "ERROR": ERROR,
    "WARNING": WARNING,
    "WARN": WARN,
    "INFO": INFO,
    "DEBUG": DEBUG,
    "NOTSET": NOTSET,
}

LEVEL_TO_NAME = {
    CRITICAL: "CRITICAL",
    FATAL: "FATAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG",
    NOTSET: "NOTSET",
}

LOG_DATE_FORMAT_DEBUG = "%Y-%m-%d %H:%M:%S"
LOG_DATE_FORMAT_INFO = "%H:%M:%S"

LOG_FORMAT_DEBUG = (
    "%(asctime)s.%(msecs)d | %(levelname)9s | %(pathname)s:%(lineno)d - %(message)s"
)
LOG_FORMAT_INFO = "%(asctime)s | %(levelname)9s | %(name)s - %(message)s"

LOG_FORMATTER_CONVERTER_DEBUG = time.gmtime
LOG_FORMATTER_CONVERTER_INFO = time.localtime

LOG_FILE_MODE = "a"
LOG_FILE_ENCODING = "latin1"
LOG_FILE_DELAY = False

FormatterConverter = Callable[[int], time.struct_time]


def to_level(value: Any) -> Optional[int]:
    """Cconvert any value to log-level integer or None.

    Args:
        value: Any object.

    Returns:
        Integer that is a valid log-level upon success, None otherwise.

    Examples:

        >>> to_level("DEBUG") == logging.DEBUG
        True
        >>> to_level("info") == logging.INFO
        True
        >>> to_level("wArN") == logging.WARNING
        True
        >>> to_level(" No t Set ") == logging.NOTSET
        True
        >>> to_level(40) == logging.ERROR
        True
        >>> to_level("what") is None
        True
        >>> to_level(-20) is None
        True
        >>> to_level("") is None
        True
        >>> to_level("nOne") is None
        True
        >>> to_level(None) is None
        True
    """

    if isinstance(value, int):
        return value if (value in LEVEL_TO_NAME) else None

    if isinstance(value, str):
        value = re.sub(r"[^a-zA-Z]", "", value, re.IGNORECASE | re.DOTALL)
        value = value.upper()

        if value == "NONE":
            return None

        if value in NAME_TO_LEVEL:
            return NAME_TO_LEVEL[value]

        try:
            return to_level(int(value))
        except ValueError:
            return None

    return to_level(str(value))


def get_log_format(level: Any) -> str:
    """Get the log-format for the given level.

    Args:
        level: Log-level name of value.

    Returns:
        String with the log-format.
    """

    level = to_level(level)
    return LOG_FORMAT_INFO if (level == INFO) else LOG_FORMAT_DEBUG


def get_log_date_format(level: Any) -> str:
    """Get the log-date-format for the given level.

    Args:
        level: Log-level name of value.

    Returns:
        String with the log-date-format.
    """

    level = to_level(level)
    return LOG_DATE_FORMAT_INFO if (level == INFO) else LOG_DATE_FORMAT_DEBUG


def get_log_formatter_converter(level: Any) -> FormatterConverter:
    """Get Formatter converter func for the given level.

    Args:
        level: Log-level name of value.

    Returns:
        The converter function.
    """

    level = to_level(level)
    if level == INFO:
        return LOG_FORMATTER_CONVERTER_INFO
    return LOG_FORMATTER_CONVERTER_DEBUG


def create_formatter(level: Any) -> logging.Formatter:
    """Create Formatter for the given level.

    Args:
        level: Log-level name of value.

    Returns:
        The newly-created Formatter instance.
    """

    # process args
    fmt = get_log_format(level)
    datefmt = get_log_date_format(level)
    converter = get_log_formatter_converter(level)

    # create and configure the Formatter
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    formatter.converter = converter

    return formatter


def create_file_handler(
    file: Union[str, PathLike, Path],
    mode: Optional[str] = None,
    encoding: Optional[str] = None,
    delay: Optional[bool] = None,
) -> logging.FileHandler:
    """Creates and returns new FileHandler with the given settings.

    Args:
        file: Target file.
        mode: File mode (default: 'a').
        encoding: File encoding (default: 'latin1').
        delay: File delay (default: False).

    Returns:
        The newly-created FileHandler instance.
    """

    # process args
    file_path = Path(file).absolute().resolve(strict=False)
    file_dir = file_path.parent
    file_name = str(file_path)

    mode = LOG_FILE_MODE if (mode is None) else mode
    delay = LOG_FILE_DELAY if (delay is None) else delay
    encoding = LOG_FILE_ENCODING if (encoding is None) else encoding

    # ensure the file's parent folder exists
    if file_dir.exists() and (not file_dir.is_dir()):
        raise NotADirectoryError(file_dir)
    file_dir.mkdir(parents=True, exist_ok=True)

    # create and configure the FileHandler
    handler = logging.FileHandler(file_name, mode, encoding, delay)
    atexit.register(handler.flush)
    atexit.register(handler.close)

    return handler


def remove_handlers(logger: logging.Logger) -> NoReturn:
    """Removes all handlers from the given logger.

    Args:
        logger: Target logger.
    """

    handlers = list(logger.handlers)
    for handler in handlers:
        handler.flush()
        handler.close()
        logger.removeHandler(handler)


def add_file_handler(
    logger: logging.Logger, file: Union[str, PathLike, Path], level: Any
) -> logging.FileHandler:
    """Creates a new FileHandler, adds it to the given Logger and returns it."""

    # process args
    log_level = to_level(level)

    # create Formatter
    formatter = create_formatter(log_level)

    # create and configure FileHandler
    handler = create_file_handler(file)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    # attach FileHandler to the Logger
    logger.addHandler(handler)
    atexit.register(logger.removeHandler, handler)

    return handler


def init_logging(
    level: Any,
    *,
    stream: Optional[TextIO] = sys.stdout,
    file: Optional[Union[str, PathLike, Path]] = None
) -> NoReturn:
    """Initialize the global logging framework with the settings."""

    log_level = to_level(level)
    log_stream = stream
    log_format = get_log_format(log_level)
    log_date_format = get_log_date_format(log_level)

    formatter_converter = get_log_formatter_converter(log_level)
    logging.Formatter.converter = formatter_converter

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=log_date_format,
        stream=log_stream,
    )

    if file is not None:
        root_logger = logging.getLogger()
        add_file_handler(root_logger, file, log_level)

    atexit.register(logging.shutdown)
