"""This module contains logic for dealing with dates and times."""
import logging
import warnings
from typing import List, NamedTuple

from dateutil import rrule
from pandas import Timestamp
from recurrent import RecurringEvent

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def is_normalized(stamp: Timestamp) -> bool:
    """Checks if a Timestamp is normalized.

    Args:
        stamp: Timestamp instance.

    Returns:
        True if the stamp points exactly at midnight, false otherwise.

    Raises:
        TypeError: Raised if the stamp is not a Timestamp instance.
    """

    if not isinstance(stamp, Timestamp):
        raise TypeError(stamp, Timestamp, type(stamp))

    return (
            (stamp.hour == 0)
            and (stamp.minute == 0)
            and (stamp.second == 0)
            and (stamp.microsecond == 0)
    )


def parse_time_stamp(value) -> Timestamp:
    """Attempts to parse time-stamp from any value.

    Args:
        value: Any value that can be parsed to Timestamp by Pandas.

    Returns:
        Timestamp instance.

    Raises:
        ValueError: raised if the value could not be parsed to a date.
    """

    if value is None:
        raise ValueError(value)

    if isinstance(value, Timestamp):
        return value

    try:
        return Timestamp(value)
    except Exception as ex:
        raise ValueError(value) from ex


def parse_date_stamp(value) -> Timestamp:
    """Attempts to parse date-stamp from any value.

    Args:
        value: Any value that can be parsed to Timestamp by Pandas.

    Returns:
        Normalized Timestamp instance (pointing to midnight) or raises.

    Raises:
        ValueError: raised if the value could not be parsed.
    """

    time_stamp = parse_time_stamp(value)

    if is_normalized(time_stamp):
        return time_stamp

    return time_stamp.normalize()


def generate_date_stamps(frequency, start_date, end_date) -> List[Timestamp]:
    """Generate list of date-stamps with the given frequency.

    Args:
        frequency: Sentence describing the frequency.
        start_date: The start date of the period.
        end_date: The end date of the period.

    Returns:
        List of normalized Timestamp with the given frequency inside the period.

    Raises:
        ValueError: raised if the dates or the frequency could not be parsed.
    """

    try:
        return [parse_date_stamp(frequency)]
    except ValueError:
        pass

    try:
        start = parse_date_stamp(start_date)
        end = parse_date_stamp(end_date)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            event = RecurringEvent()
            event.parse(frequency)
            rule = rrule.rrulestr(event.get_RFC_rrule())

        return [
            Timestamp(occurrence).normalize()
            for occurrence
            in rule.between(start, end, inc=True)
        ]

    except Exception as ex:
        raise ValueError(frequency) from ex


def stamp_to_str(stamp: Timestamp) -> str:
    """Converts Timestamp to string.

    If the Timestamp is 'normalized' the resulting string is in ISO-dateformat,
    otherwise the result from the default Timestamp implementation is returned.

    Args:
        stamp: Timestamp instance.

    Returns:
        The resulting string.
    """

    if is_normalized(stamp):
        return str(stamp.date())

    return str(stamp)


class Period(NamedTuple):
    """Represents the period of time between two Timestamps."""

    start: Timestamp
    end: Timestamp

    def __str__(self) -> str:
        start = stamp_to_str(self.start)
        end = stamp_to_str(self.end)
        return f"['{start}' - '{end}']"

    def generate_dates(self, frequency: str) -> List[Timestamp]:
        """Generates list of dates in the period with the given frequency.

        Args:
            frequency: Sentence describing the frequency.

        Returns:
            List of normalized Timestamps or raises.

        Raises:
            ValueError: raised if the frequency could not be parsed.
        """

        return generate_date_stamps(frequency, self.start, self.end)
