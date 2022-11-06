"""Config used by the pytest runner."""
import logging

KNOWN_LIBRARY_LOGGERS = [
    "matplotlib.font_manager",
    "parsedatetime",
    "PIL.PngImagePlugin",
    "recurrent",
]

# disable known library loggers that flood the log
for _logger_name in KNOWN_LIBRARY_LOGGERS:
    _logger = logging.getLogger(_logger_name)
    _logger.disabled = True
