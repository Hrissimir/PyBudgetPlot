"""Config used by the pytest runner."""
import logging

KNOWN_LIBRARY_LOGGERS = [
    "recurrent",
    "matplotlib.font_manager",
    "PIL.PngImagePlugin",
]

# disable known library loggers that flood the log
for _logger_name in KNOWN_LIBRARY_LOGGERS:
    _logger = logging.getLogger(_logger_name)
    _logger.disabled = True
