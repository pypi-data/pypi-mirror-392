import calendar
import datetime
from enum import Enum

from ratisbona_utils.languages.english import encode_english_short_ordinal
from ratisbona_utils.monads import Maybe, Nothing, Just


class DDateWeekday(str, Enum):
    SWEETMORN = 'Sweetmorn'
    BOOMTIME = 'Boomtime'
    PUNGENDAY = 'Pungenday'
    PRICKLEPRICKLE = 'Prickle-Prickle'
    SETTHERSDAY = 'Setting Orange'


class DDateSeason(str, Enum):
    CHAOS = 'Chaos'
    DISCORD = 'Discord'
    CONFUSION = 'Confusion'
    BUREAUCRACY = 'Bureaucracy'
    THE_AFTERMATH = 'The Aftermath'


def maybe_get_discordian_weekday(a_date: datetime.date) -> Maybe[DDateWeekday]:
    """
    Returns the discordian weekday for the given date.

    Args:
        a_date: The date to get the weekday for.

    Returns:
        The discordian weekday for the given date or None if the given date is St. Tib's day.
    """
    days_since_jan_first = _maybe_get_st_tibs_day_corrected_daycount(a_date)
    if not days_since_jan_first:
        return Nothing
    return Just(list(DDateWeekday)[days_since_jan_first.unwrap_value() % 5])


def _get_st_tibs_day_relation(a_date: datetime.date) -> Maybe[int]:
    """
    Returns the relation between the given date and the St. Tib's day.

    Args:
        a_date: The date to check the relation to St. Tib's day for.

    Returns:
        None if the given year is not a leap year.
        -1 if the given date is before St. Tib's day.
        0 if the given date is St. Tib's day.
        1 if the given date is after St. Tib's day.
    """
    if not calendar.isleap(a_date.year):
        return Nothing

    st_tibs_day = datetime.date(a_date.year, 2, 29)

    if a_date < st_tibs_day:
        return Just(-1)
    elif a_date > st_tibs_day:
        return Just(1)
    return Just(0)


def _maybe_get_st_tibs_day_corrected_daycount(a_date: datetime.date) -> Maybe[int]:
    """
        Returns the corrected day count since January 1st for the given date (corrected for St. Tib's day).

        Args:
            a_date: The date to get the corrected day count for.

        Returns:
            None if the given day is St. Tib's day.
            The corrected day count since January 1st otherwise (St. Tib's day does not count as day).
            Result is useful for calculating the discordian season and day.
    """
    days_since_jan_first = (a_date - datetime.date(a_date.year, 1, 1)).days
    relation = _get_st_tibs_day_relation(a_date)
    if relation and relation == 0:
        return Nothing
    if relation and relation == 1:
        days_since_jan_first -= 1
    return Just(days_since_jan_first)


def maybe_get_discordian_season_and_day(a_date: datetime.date) -> tuple[Maybe[DDateSeason], Maybe[int]]:
    """
        Returns the discordian season and day for the given date.

        Args:
            a_date: The date to get the discordian season and day for.

        Returns:
            A tuple containing the discordian season and day for the given date.
            If the given date is St. Tib's day, the result is (None, None).
    """
    maybe_days_since_jan_first = _maybe_get_st_tibs_day_corrected_daycount(a_date)
    if not maybe_days_since_jan_first:
        return Nothing, Nothing
    days_since_jan_first = maybe_days_since_jan_first.unwrap_value()
    the_season: DDateSeason = list(DDateSeason)[days_since_jan_first // 73]
    the_day = days_since_jan_first % 73 + 1
    return Just(the_season), Just(the_day)


def yold_by_date(date: datetime.date) -> int:
    """
        Returns the YOLD for the given date.

        Args:
            date: The date to get the YOLD for.

        Returns:
            The YOLD for the given date.
    """
    return date.year + 1166


def ddate(dday: Maybe[int], season: Maybe[DDateSeason], weekday: Maybe[DDateWeekday], yold: int) -> str:
    """
        Formats the discordian date as a string. Does not check if the given date is valid (e.g. St. Tib's day
        in a non-leap year/yold).

        Args:
            dday: The day of the season (1-73). Pass None if the given date is St. Tib's day.
            season: The season. Pass None if the given date is St. Tib's day.
            weekday: The weekday. Pass None if the given date is St. Tib's day.
            yold: The YOLD.
    """

    if not weekday or not dday or not season:
        return f'Today is St. Tib\'s Day in the YOLD {yold}'

    return \
        f'Today is {weekday.unwrap_value().value}, the {encode_english_short_ordinal(dday.unwrap_value())} of {season.unwrap_value().value} ' \
        f'in the YOLD {yold}'


def decode(dayOfSeason: Maybe[int], season: Maybe[DDateSeason], yold: int) -> datetime.date:
    """
    Returns the date for the given discordian season and day.
    """
    if not dayOfSeason or not season:
        return datetime.date(yold-1166, 2, 29)  # St. Tib's day!

    ordinal_of_season = list(DDateSeason).index(season.unwrap_value())

    preliminary_date = (
        datetime.date(yold-1166, 1, 1)
        + datetime.timedelta(days=(ordinal_of_season * 73 + dayOfSeason.unwrap_value() - 1))
    )

    if (
            calendar.isleap(preliminary_date.year)
            and preliminary_date >= datetime.date(preliminary_date.year, 2, 29)
    ):
        return preliminary_date + datetime.timedelta(days=1)

    return preliminary_date



