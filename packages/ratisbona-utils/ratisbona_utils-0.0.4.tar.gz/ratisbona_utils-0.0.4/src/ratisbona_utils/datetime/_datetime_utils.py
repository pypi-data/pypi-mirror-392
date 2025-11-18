import re
from calendar import monthrange
from datetime import time, date, datetime, timedelta, timezone
from typing import Iterator, Callable

from dateutil.tz import tzlocal

from ratisbona_utils.monads import Maybe, Just, Nothing

DateTimeLike = datetime | date | time
NowProvider = Callable[[], datetime]

def to_last_weekday(a_date: date, weekday: int) -> timedelta:
    """
    Converts a date to the last occurrence of the specified weekday before or on that date.

    Args:
        a_date: The date to convert.
        weekday: The target weekday (0=Monday, 6=Sunday).

    Returns:
        date: The last occurrence of the specified weekday before or on the given date.
    """
    days_to_subtract = (a_date.weekday() - weekday) % 7
    return timedelta(days=-days_to_subtract)

def to_next_weekday(a_date: date, weekday: int) -> timedelta:
    """
    Converts a date to the next occurrence of the specified weekday after or on that date.

    Args:
        a_date: The date to convert.
        weekday: The target weekday (0=Monday, 6=Sunday).

    Returns:
        date: The next occurrence of the specified weekday after or on the given date.
    """
    days_to_add = (weekday - a_date.weekday()) % 7
    return timedelta(days=days_to_add)

def maybe_extract_date(a_datetime_like: DateTimeLike) -> Maybe[date]:
    """
    Extracts a date from a datetime-like object if possible.

    Args:
        a_datetime_like: A datetime, date, or time object.

    Returns:
        Maybe[date]: Just(date) if a date can be extracted, Nothing otherwise.
    """
    if isinstance(a_datetime_like, datetime):
        return Just(a_datetime_like.date())
    if isinstance(a_datetime_like, date):
        return Just(a_datetime_like)
    return Nothing

def maybe_extract_time(a_datetime_like: DateTimeLike) -> Maybe[time]:
    """
    Extracts a time from a datetime-like object if possible.

    Args:
        a_datetime_like: A datetime, date, or time object.

    Returns:
        Maybe[time]: Just(time) if a time can be extracted, Nothing otherwise.
    """
    if isinstance(a_datetime_like, datetime):
        return Just(a_datetime_like.time())
    if isinstance(a_datetime_like, time):
        return Just(a_datetime_like)
    return Nothing

def ensure_datetime(a_datetime_like: DateTimeLike, now_provider: NowProvider) -> datetime:
    if isinstance(a_datetime_like, datetime):
        return a_datetime_like
    if isinstance(a_datetime_like, date):
        return to_datetime(a_datetime_like)
    if isinstance(a_datetime_like, time):
        return datetime.combine(now_provider().date(), a_datetime_like)
    raise TypeError(f"Unsupported type for datetime conversion: {type(a_datetime_like)}. ")

def ensure_timezone(a_datetime: datetime) -> datetime:
    if a_datetime.tzinfo is None:
        return a_datetime.replace(tzinfo=tzlocal())
    return a_datetime

def ensure_no_timezone(a_datetime: datetime) -> datetime:
    return a_datetime.replace(tzinfo=None)

def to_datetime(a_date: date) -> datetime:
    return datetime.combine(a_date, time.min)

def format_ms_HHMMSSss(time_elapsed_millis: int, show_msec: bool = True) -> str:
    """
        Formats a time in milliseconds to a string in the format `HH:MM:SS.mmm`.
    """
    raw_secs, milliseconds = divmod(time_elapsed_millis, 1000)
    raw_min, seconds = divmod(raw_secs, 60)
    hours, minutes = divmod(raw_min, 60)
    retval = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    if show_msec:
        retval += f".{milliseconds:03d}"
    return retval


def last_day_of_month(given_date: date) -> date:
    """
        Gives the last day of the month of the given date.
        Bitterly missed in the standard library for the actual datatype date, no reason aparent, why they combined
        the int-typed version with unrelated stuff to monthrange...

        Args:
            given_date: date, the date for which the last day of the month is requested.

        Returns:
            date: The last day of the month of the given date.
    """
    last_day = monthrange(given_date.year, given_date.month)[1]
    return date(given_date.year, given_date.month, last_day)


def month_iterator(start: date, end: date) -> Iterator[tuple[int, int]]:
    """
    Provides an iterator that advances month by month from start (inclusive) to end (exclusive) and yields year and month number.

    Args:
        start: date, the day the iterator should start (inclusive).
        end: date, the day the iterator should end (exclusive).

    Returns:
        Tuple[int, int]: Year and month, e.g. (2020, 1) for January 2020.
    """
    current = start.replace(day=1)
    while current < end:
        yield current.year, current.month
        current = (current + timedelta(days=32)).replace(day=1)

def try_parse_leading_isodatetime(value: str) -> Maybe[tuple[datetime, str]]:
    """
    Tries to parse a datetime in the format 'YYYY-MM-DDTHH:MM:SS' from the beginning of the given string.

    Args:
        value: str, the string to parse.

    Returns:
        Maybe[datetime]: The parsed datetime or nothing if the string does not start with a valid datetime.
    """

    match = re.match(
        r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})[T ]"
        r"(?P<hour>\d{2}):(?P<minute>\d{2})"
        r"(:(?P<second>\d{2}))?"
        r"(\.(?P<millisecond>\d+))?"
        r"(?P<timezone>Z|[+-]\d{2}:\d{2})?",
        value
    )

    if not match:
        return Nothing

    groups = match.groupdict()

    # Convert matched values to integers where applicable
    year = int(groups["year"])
    month = int(groups["month"])
    day = int(groups["day"])
    hour = int(groups["hour"])
    minute = int(groups["minute"])
    second = int(groups["second"]) if groups["second"] else 0
    microsecond = int(groups["millisecond"].ljust(6, "0")) if groups["millisecond"] else 0  # Ensure 6 digits
    rest = value[match.end():]

    # Handle timezone conversion
    tz_str = groups["timezone"]
    if tz_str:
        if tz_str == "Z":
            tz = timezone.utc
        else:
            sign = 1 if tz_str[0] == "+" else -1
            tz_hour, tz_minute = map(int, tz_str[1:].split(":"))
            tz = timezone(timedelta(hours=tz_hour * sign, minutes=tz_minute * sign))
    else:
        tz = None  # No timezone present

    # Create datetime object
    return Just((
        datetime(year, month, day, hour, minute, second, microsecond, tzinfo=tz),
        rest
    ))


def try_parse_leading_isodate(value: str) -> Maybe[tuple[date, str]]:
    """
    Tries to parse a date in the format 'YYYY-MM-DD' from the beginning of the given string.

    Args:
        value: str, the string to parse.

    Returns:
        Maybe[date]: The parsed date or nothing if the string does not start with a valid date.
    """
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})(.*)", value)
    if not match:
        return Nothing
    year, month, day = map(int, match.groups()[0:3])
    rest = match.groups()[3]
    try:
        return Just((date(year, month, day), rest))
    except ValueError:
        return Nothing
