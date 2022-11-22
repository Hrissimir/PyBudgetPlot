"""This module defines the data and logic for processing a period definition."""
import warnings
from typing import Any, Dict, List

from dateutil import rrule
from pandas import Timestamp
from recurrent import RecurringEvent


def is_datestamp(stamp: Timestamp) -> bool:
    """Checks if a ``Timestamp`` is normalized (e.g. 'date-stamp').

    Args:
        stamp: Timestamp instance.

    Returns:
        True if the stamp contains only date-related data, False otherwise.

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


def parse_timestamp(value: Any) -> Timestamp:
    """Parse any value to ``Timestamp`` instance.

    If the value is already a ``Timestamp``, the same object is returned.

    If the value is ``int`` or ``float``, it's treated as UTC-based POSIX stamp.

    Args:
        value: Any value that can be parsed to Timestamp.

    Returns:
        The parsed Timestamp instance or raises.

    Raises:
        ValueError: Raised if the value is None or if it could not be parsed.
    """

    if value is None:
        raise ValueError("Can't parse None to Timestamp!")

    if isinstance(value, Timestamp):
        return value

    try:
        if isinstance(value, (int, float)):
            return Timestamp.utcfromtimestamp(value)
        return Timestamp(value)
    except Exception as ex:
        raise ValueError(f"Error while parsing {value!r} to Timestamp!") from ex


def parse_datestamp(value: Any) -> Timestamp:
    """Parse any value to normalized ``Timestamp`` (e.g. 'date-stamp').

    Args:
        value: Any value that can be parsed to Timestamp by `parse_timestamp`.

    Returns:
          Timestamp instance with only date-related data or raises.

    Raises:
         ValueError: Raised if the value is None or could not be parsed.
    """

    if isinstance(value, Timestamp):
        stamp = value
    else:
        stamp = parse_timestamp(value)

    return stamp if is_datestamp(stamp) else stamp.normalize()


def format_stamp(stamp: Timestamp) -> str:
    """Formats a ``Timestamp`` instance to string using ISO format.

    If the stamp is 'date-stamp', the result is as if calling `date.isoformat`,
    otherwise the result is as if `datetime.isoformat` was called.

    Args:
        stamp: Timestamp instance.

    Returns:
        String containing date or datetime in ISO format.

    Raises:
        TypeError: Raised if the stamp is not a Timestamp instance.
    """

    if is_datestamp(stamp):
        return stamp.date().isoformat()
    return stamp.isoformat()


class Period:
    """Represents the fixed period of time between 'start' and 'end' stamps."""

    def __init__(self, start: Any, end: Any):
        self.start = parse_timestamp(start)
        self.end = parse_timestamp(end)

    def __eq__(self, other) -> bool:
        if isinstance(other, Period):
            return (self.start == other.start) and (self.end == other.end)
        return False

    def __repr__(self) -> str:
        return f"{type(self).__name__}(start={self.start!r}, end={self.end!r})"

    def __str__(self) -> str:
        start_str = format_stamp(self.start)
        end_str = format_stamp(self.end)
        return f"['{start_str}' - '{end_str}']"

    def as_dict(self) -> Dict[str, str]:
        return {
            "start": format_stamp(self.start),
            "end": format_stamp(self.end),
        }

    def generate_datestamps(self, frequency: str) -> List[Timestamp]:
        """Generates a list of 'date-stamps' with the given frequency.

        Args:
            frequency: Sentence describing the frequency, or date in ISO-format.

        Returns:
            List of normalized Timestamps referring to dates in the Period.

        Raises:
            TypeError: Raised if the frequency is not a string instance.
            ValueError: Raised if the frequency could not be parsed.
        """

        if not isinstance(frequency, str):
            raise TypeError(frequency, str, type(frequency))

        try:
            # check if the frequency can be parsed to a single date-stamp.
            result = [parse_datestamp(frequency)]
        except ValueError:
            result = None

        if result is None:

            # ensure that `date-stamps` are used for the calculations
            start_date = parse_datestamp(self.start)
            end_date = parse_datestamp(self.end)

            try:
                # silence `parsedatetime` warning due bad call from `recurrent`
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")

                    event = RecurringEvent(now_date=start_date)
                    event.parse(frequency)

                    rfc_rrule = event.get_RFC_rrule()
                    rule = rrule.rrulestr(rfc_rrule, dtstart=start_date)

                    result = [
                        Timestamp(occurrence).normalize()
                        for occurrence
                        in rule.between(start_date, end_date, inc=True)
                    ]

            except Exception as ex:
                raise ValueError(frequency) from ex

        return result
