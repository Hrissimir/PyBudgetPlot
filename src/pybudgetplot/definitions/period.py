"""This module defines the data and logic for processing a period definition."""
import logging
import warnings
from datetime import date, datetime
from typing import List, NamedTuple

from dateutil import rrule
from pandas import Timestamp
from recurrent import RecurringEvent

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

PARSABLE_STAMP_TYPES = (int, str, date, datetime, Timestamp)


def is_datestamp(stamp: Timestamp) -> bool:
    """Checks if a Timestamp is normalized (e.g. 'date-stamp').

    Args:
        stamp: Timestamp instance.

    Returns:
        True if the Timestamp contains only date-related data, False otherwise.

    Raises:
        TypeError: Raised if the 'stamp' param is not a Timestamp instance.
    """

    _log.debug("is_datestamp - stamp: '%s'", stamp)

    if not isinstance(stamp, Timestamp):
        _log.warning("is_datestamp - unsupported param-type!")
        raise TypeError(stamp, Timestamp, type(stamp))

    result = (
            (stamp.hour == 0)
            and (stamp.minute == 0)
            and (stamp.second == 0)
            and (stamp.microsecond == 0)
    )

    _log.debug("is_datestamp - result: '%s'", result)
    return result


def parse_datestamp(value) -> Timestamp:
    """Parse a value to a 'normalized' Timestamp (e.g. 'date-stamp').

    Args:
        value: Any value that can be parsed to Timestamp by Pandas.

    Returns:
          Timestamp instance pointing to midnight of a given date.

    Raises:
         TypeError: Raised if the param type is not supported.
         ValueError: Raised if the value could not be parsed.
    """

    _log.debug("parse_datestamp - value: '%s'", value)

    if not isinstance(value, PARSABLE_STAMP_TYPES):
        raise TypeError(value, PARSABLE_STAMP_TYPES, type(value))

    if isinstance(value, Timestamp):
        result = value
    else:
        try:
            result = Timestamp(value)
        except Exception as ex:
            _log.warning("parse_datestamp - failed to parse by all means!")
            raise ValueError(value) from ex

    if not is_datestamp(result):
        result = result.normalize()

    _log.debug("parse_datestamp - result: '%s'", result)
    return result


def format_timestamp(stamp: Timestamp) -> str:
    """Format a Timestamp to string.

    If the Timestamp is 'normalized', the resulting string is in ISO-dateformat,
    otherwise the result of the default Timestamp.__str__() is returned.

    Args:
        stamp: Timestamp instance.

    Returns:
        The resulting string.
    """

    _log.debug("format_timestamp - stamp: '%s'", stamp)

    if is_datestamp(stamp):
        result = stamp.date().isoformat()
    else:
        result = str(stamp)

    _log.debug("format_timestamp - result: '%s'", result)
    return result


class Period(NamedTuple):
    """Represent all dates in the period between the start-date and end-date."""

    start_date: Timestamp
    end_date: Timestamp

    def __str__(self) -> str:
        start = format_timestamp(self.start_date)
        end = format_timestamp(self.end_date)
        return f"['{start}' - '{end}']"

    def as_dict(self) -> dict:
        """Converts the current Period instance to dict.

        Returns:
            Dict with the period data, whose values are the dates in ISO-format.
        """

        return {
            "start_date": format_timestamp(self.start_date),
            "end_date": format_timestamp(self.end_date),
        }

    def generate_dates(self, frequency: str) -> List[Timestamp]:
        """Generate a list of dates in the period with the given frequency.

        Args:
            frequency: Sentence describing a frequency or date in ISO-format.

        Returns:
            List of normalized Timestamps referring to dates in the period.

        Raises:
            ValueError: Raised if the frequency could not be parsed.
        """

        _log.debug("generate_dates - frequency: '%s'", frequency)

        # check to see if the frequency can be parsed to a single date.
        try:
            result = [parse_datestamp(frequency)]
        except ValueError:
            result = None

        if result is None:

            # try to parse the frequency using the 'recurrent' lib
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    event = RecurringEvent()
                    event.parse(frequency)
                    rule = rrule.rrulestr(event.get_RFC_rrule())

                    # ensure all Timestamps are normalized.
                    result = [
                        Timestamp(occurrence).normalize()
                        for occurrence
                        in rule.between(
                            self.start_date, self.end_date, inc=True
                        )
                    ]

            except Exception as ex:
                _log.warning("generate_dates - the frequency could not parsed!")
                raise ValueError(frequency) from ex

        _log.debug("generate_dates - got [%s] dates: '%s'", len(result), result)
        return result


def new_period(start, end) -> Period:
    """Helper method for creating new Period instances.

    Parses the args to Timestamp objects before passing them to the constructor.

    Args:
        start: Value for the period's start-date.
        end: Value for the period's end-date.

    Returns:
        Period instance whose start-date and end-date are normalized Timestamps.

    Raises:
        ValueError: Raised if the args could not be parsed to Timestamp objects.
    """

    _log.debug("new_period - start: '%s', end: '%s'", start, end)
    start_date = parse_datestamp(start)
    end_date = parse_datestamp(end)
    result = Period(start_date, end_date)
    _log.debug("new_period - result: '%s'", result)
    return result
