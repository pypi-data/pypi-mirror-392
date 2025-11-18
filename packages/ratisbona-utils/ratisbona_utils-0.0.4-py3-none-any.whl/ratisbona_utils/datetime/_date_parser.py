from datetime import datetime, date, time, timedelta
from typing import Sequence

from ratisbona_utils.datetime._date_tokenizer import token_definitions
from ratisbona_utils.datetime._datetime_utils import to_last_weekday, to_next_weekday
from ratisbona_utils.functional import first, Provider
from ratisbona_utils.monads import Just, Maybe, Error, Nothing
from ratisbona_utils.monads.monads2 import with_errorhandling
from ratisbona_utils.parsing import get_tokenizer, Token

DEBUG = True


if DEBUG:

    def dprint(*args, **kwargs):
        print(*args, **kwargs)

else:

    def dprint(*args, **kwargs):
        pass


lenient_tokenizer = get_tokenizer(token_definitions)


def lenient_parse_year(
    year_str: str, two_digit_year_century_provider: Provider[datetime] = datetime.now
) -> Maybe[int | ValueError]:
    """
    Leniently parse a year string that may have 2 or 4 digits.
    Args:
        year_str: the year string to parse
        two_digit_year_century_provider: Provider of datetime. This datetime is used to determine the century for 2-digit years.

    Returns:
        Maybe[int | ValueError]: Just(year) if parsing was successful, Error(ValueError) otherwise.

    """
    if len(year_str) == 2:
        now = two_digit_year_century_provider()
        current_year = now.year
        current_century = current_year // 100
        current_centuries_year = current_year % 100
        year_int = int(year_str)
        if year_int > current_centuries_year:
            current_century -= 1
        current_century_str = str(current_century)
        current_century_prefix = current_century_str[:2]
        year_str = current_century_prefix + year_str
    if len(year_str) != 4:
        return Error(ValueError(f"Year must have 2 or 4 digits, but got '{year_str}'"))
    try:
        year_int = int(year_str)
    except ValueError:
        return Error(ValueError(f"Year must be a number, but got '{year_str}'"))
    return Just(year_int)


def try_parse_datetime(token: Token) -> Maybe[datetime | ValueError]:
    """
    Try to parse a datetime from a token like the lenient tokenizer produces, that means it is of type 'Datetime'
    and it has to contain the fields:
        - year
        - month
        - day
        - hour
        - minute
        - second (optional, defaults to 0)
        - millisecond (optional, defaults to 0)

    Note that returning Errors might indicate simply that the token is of another type and another parsing
    function should be tried.

    Args:
        token: A lenient tokenizer like token of type 'Datetime'.

    Returns:
        Maybe[datetime | ValueError]: Just(datetime) if parsing was successful, Error(ValueError) otherwise.

    Returns ValueError if:
        - The token is not of type 'Datetime'.
        - Any of the required fields are missing or cannot be converted to int.

    """
    if token.token_type_name != "Datetime":
        return Error(
            ValueError(
                f"Token is not a datetime token: {token}. Expected Type 'Datetime' but got '{token.token_type_name}'"
            )
        )
    maybe_match_groups = Just(
        token.token_match_groups
    )  # Will throw for a Datetime Token without match groups!
    maybe_year = maybe_match_groups["year"].bind(int)
    maybe_month = maybe_match_groups["month"].bind(int)
    maybe_day = maybe_match_groups["day"].bind(int)
    maybe_hour = maybe_match_groups["hour"].bind(int)
    maybe_minute = maybe_match_groups["minute"].bind(int)
    maybe_second = maybe_match_groups["second"].bind(int).default_or_error(0)
    maybe_microseconds = (
        maybe_match_groups["millisecond"]
        .bind(int)
        .default_or_error(0)
        .bind(lambda millisecond: millisecond * 1000)
    )
    return with_errorhandling(
        datetime,
        maybe_year,
        maybe_month,
        maybe_day,
        maybe_hour,
        maybe_minute,
        maybe_second,
        maybe_microseconds,
    )


def try_parse_date(
    token: Token, implicit_year_provider: Provider[datetime] = datetime.now
) -> Maybe[date | ValueError]:
    """
    Try to parse a date from a token like the lenient tokenizer produces, that means it is of type 'Date'
    and it has to contain the fields:
        - year (optional, maybe 2 maybe 4 digits, defaults year from now_provider)
        - month
        - day

    Args:
        token: The lenient tokenizer like token of type 'Date'.
        implicit_year_provider: The provider of the current datetime, used to get the current year if the year is missing.

    Returns:

    """
    if token.token_type_name != "Date":
        return Error(
            ValueError(
                f"Token is not a date token: {token}. Expected Type 'Date' but got '{token.token_type_name}'"
            )
        )
    maybe_match_groups = Just(
        token.token_match_groups
    )  # Will throw for a Date Token without match groups!
    maybe_year = (
        maybe_match_groups["year"]
        .bind(lenient_parse_year, implicit_year_provider)
        .default_or_error(implicit_year_provider().year)
    )
    maybe_month = maybe_match_groups["month"].bind(int)
    maybe_day = maybe_match_groups["day"].bind(int)
    return with_errorhandling(date, maybe_year, maybe_month, maybe_day)


def try_parse_time(token: Token) -> Maybe[time | ValueError]:
    """
    Try to parse a time from a token like the lenient tokenizer produces, that means it is of type 'Time'
    and it has to contain the fields:
        - hour
        - minute
        - second (optional, defaults to 0)
        - millisecond (optional, defaults to 0)

    Args:
        token: A lenient tokenizer like token of type 'Time'.

    Returns:
        Maybe[time | ValueError]: Just(time) if parsing was successful, Error(ValueError) otherwise.

    """
    if token.token_type_name != "Time":
        return Error(
            ValueError(
                f"Token is not a time token: {token}. Expected Type 'Time' but got '{token.token_type_name}'"
            )
        )
    maybe_match_groups = Just(
        token.token_match_groups
    )  # Will throw for a Time Token without match groups!
    maybe_hour = maybe_match_groups["hour"].bind(int)
    maybe_minute = maybe_match_groups["minute"].bind(int)
    maybe_second = maybe_match_groups["second"].bind(int).default_or_error(0)
    maybe_microseconds = (
        maybe_match_groups["millisecond"]
        .bind(int)
        .default_or_error(0)
        .bind(lambda millisecond: millisecond * 1000)
    )
    return with_errorhandling(
        time, maybe_hour, maybe_minute, maybe_second, maybe_microseconds
    )


def try_parse_relative_date(
    token: Token, relative_to_now_provider: Provider[datetime] = datetime.now
) -> Maybe[date | ValueError]:
    """
    Parses a relative date token and returns the corresponding date based on the given
    reference date provider. Handles parsing of relative terms such as "today,"
    "tomorrow," "yesterday," or specific weekdays.

    Parameters:
    token (Token): The token to parse. It must be of type 'RelativeDate', and its
                   match groups should include relevant keys for relative date processing.
    now_provider (Provider[datetime]): A callable that provides the current datetime
                                       used as point of reference for date calculations.
                                       Default is datetime.now.

    Returns:
    Maybe[date | ValueError]: Returns a Maybe-wrapped date object if parsing is
                              successful, or a Maybe-wrapped ValueError if the token
                              does not represent a valid relative date.

    Raises:
    ValueError: Raised when the input token is not of type 'RelativeDate' or contains
                unknown relative date formats.
    """
    if token.token_type_name != "RelativeDate":
        return Error(
            ValueError(
                f"Token is not a relative date token: {token}. Expected Type 'RelativeDate' but got '{token.token_type_name}'"
            )
        )
    maybe_match_groups = Just(
        token.token_match_groups
    )  # Will throw for a RelativeDate Token without match groups!
    rel = maybe_match_groups["rel"].bind(str.lower).unwrap_value()
    now = relative_to_now_provider()
    if rel in ["heute", "today"]:
        return Just(now.date())
    if rel in ["morgen", "tomorrow"]:
        return Just(now.date() + timedelta(days=1))
    if rel in ["übermorgen", "day after tomorrow"]:
        return Just(now.date() + timedelta(days=2))
    if rel in ["gestern", "yesterday"]:
        return Just(now.date() - timedelta(days=1))
    if rel in ["vorgestern", "day before yesterday"]:
        return Just(now.date() - timedelta(days=2))

    last = any([keyword in rel for keyword in ["letzter", "last"]])

    # noformat: on
    to_weekday_table = [
        (["montag", "monday", "mon", "mo"], 0),  # Monday
        (["dienstag", "tuesday", "tue", "di"], 1),  # Tuesday
        (["mittwoch", "wednesday", "wed", "mi"], 2),  # Wednesday
        (["donnerstag", "thursday", "thu", "do"], 3),  # Thursday
        (["freitag", "friday", "fri", "fr"], 4),  # Friday
        (["samstag", "saturday", "sat", "sa"], 5),  # Saturday
        (["sonntag", "sunday", "sun", "so"], 6),  # Sunday
    ]
    # noformat: off

    last_word_of_rel = rel.split()[-1].strip()
    for weekdays, weekday_index in to_weekday_table:
        if last_word_of_rel in weekdays:
            weekday_timespan_function = to_last_weekday if last else to_next_weekday
            nowdate = relative_to_now_provider()
            the_date = nowdate + weekday_timespan_function(nowdate, weekday_index)
            return Just(the_date)

    return Error(ValueError(f"Unknown relative date: '{rel}'"))


def _maybe_eat_separator_tokens(tokens: Sequence[Token]) -> tuple[Sequence[Token], list[Token]]:
    eaten_tokens = []
    while len(tokens) > 0 and tokens[0].token_type_name == "Pure Separators":
        dprint(f"Eating separator token: {tokens[0]}")
        eaten_tokens.append(tokens[0])
        tokens = tokens[1:]
    return tokens, eaten_tokens

def _format_tokenlist(tokens: Sequence[Token], separator="\n\t") -> str:
    result = ""
    for idx, token in enumerate(tokens):
        if idx > 0:
            result += separator
        result += str(token)
    return result

def leniently_parse(
    tokens: Sequence[Token],
    *,
    base_date_for_implicit_dates: Provider[datetime] = datetime.now,
    base_date_for_relative_dates: Provider[datetime] = datetime.now
) -> tuple[Maybe[date | time | datetime], Sequence[Token]]:
    """
        Facade-Routine that tries to parse a date, time or datetime from a sequence of tokens.

    """
    if len(tokens) == 0:
        return Nothing, []

    tokens = list(tokens)
    eaten_tokens = []
    next_token = tokens.pop(0)

    if next_token.token_type_name == "Datetime":
        maybe_datetime = try_parse_datetime(next_token)
        if maybe_datetime:
            dprint(f"If we found a datetime all is clear: {maybe_datetime}")
            return maybe_datetime, tokens

    maybe_date = Nothing
    if next_token.token_type_name == "Date":
        maybe_date = try_parse_date(next_token, implicit_year_provider=base_date_for_implicit_dates)

        if maybe_date:
            dprint(f"The token is a date {maybe_date}...")
            tokens, eaten_tokens = _maybe_eat_separator_tokens(tokens)
            if not tokens:
                dprint(f"...and there are no more relevant tokens, so we are done.")
                return maybe_date, eaten_tokens
            next_token = tokens.pop(0)
            dprint(
                f"...but if there are more tokens, we need to check the next token: {next_token}"
            )

    # If we did not find a date yet, we check if the next token is a relative date.
    if not maybe_date and next_token.token_type_name == "RelativeDate":
        maybe_date = try_parse_relative_date(next_token, relative_to_now_provider=base_date_for_relative_dates)
        if maybe_date:
            dprint(f"We found a relative date: {maybe_date}...")
            tokens, eaten_tokens = _maybe_eat_separator_tokens(tokens)
            if not tokens:
                dprint(
                    f"...and we consumed all the relevant tokens, now we are done."
                )
                return maybe_date, eaten_tokens
            next_token = tokens.pop(0)
            dprint(
                f"...but there are more tokens, "
                f"we need to check the next token: {next_token}"
            )

    maybe_time = Nothing
    if next_token.token_type_name == "Time":
        maybe_time = try_parse_time(next_token)
        if maybe_time:
            dprint(
                f"We found a time {maybe_time}, so we consumed the token without pulling another one."
            )
            next_token = Nothing
            eaten_tokens = []

    if next_token or eaten_tokens:
        dprint(
            "We either did not match anything or we matched and then pulled another token,\n"
            "in which case we need to put it back into the unparsed tokens."
        )

        if next_token:
            tokens.insert(0, next_token)
        for eaten_token in reversed(eaten_tokens):
            tokens.insert(0, eaten_token)
        next_token = Nothing
        eaten_tokens = []
        dprint(f"...so we put the token(s) back into the unparsed tokens:\n{_format_tokenlist(tokens)}")

    if maybe_date and maybe_time:
        the_datetime = maybe_date.bind(datetime.combine, maybe_time)
        dprint(
            f"We found a date and a time, we combine them into a datetime: {the_datetime}. Leftover tokens:\n\t{_format_tokenlist(tokens)}"
        )
        assert(len(eaten_tokens) == 0) # there can not be any eaten tokens in that case, because parse time does not skip over tokens.
        return the_datetime, tokens

    if maybe_date and not maybe_time:
        dprint(
            f"We found a date but no time, we return the date: {maybe_date}. Leftover tokens:\n\t{_format_tokenlist(tokens)}"
        )
        for eaten_token in reversed(eaten_tokens):
            tokens.insert(0, eaten_token)
        return maybe_date, tokens

    if not maybe_date and maybe_time:
        dprint(
            f"We found a time but no date, we return the time: {maybe_time}. Leftover tokens:\n\t{_format_tokenlist(tokens)}"
        )
        assert (len(eaten_tokens) == 0)  # there can not be any eaten tokens in that case, because parse time does not skip over tokens.
        return maybe_time, tokens

    print("Did not find any datelike stuff... Well, shit...")
    for eaten_token in reversed(eaten_tokens):
        tokens.insert(0, eaten_token)
    return Nothing, tokens


def ensure_datetime(
    value: datetime | date | time, now_provider: Provider[datetime] = datetime.now
) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    if isinstance(value, time):
        return datetime.combine(now_provider().date(), value)
    raise ValueError(f"Expected a datetime, date or time object, but got '{value}'")


if __name__ == "__main__":
    while True:
        print("Input:", end=" ")
        the_input = input()
        tokens = list(lenient_tokenizer(the_input))
        for token in tokens:
            print(token)

        the_parseresult = leniently_parse(tokens)
        print(the_parseresult, end="")
        print(f" {type(the_parseresult.unwrap_value())}" if the_parseresult else "")
