from ratisbona_utils.parsing import TokenDefinition, get_tokenizer
from ratisbona_utils.regexp import (
    named_matchgroup,
    any_of,
    with_word_boundaries,
    optional,
    non_capturing_group,
)

_digits_4 = r"\d{4}"
_digits_2_or_4 = r"\d{2,4}"
_digits_1_or_2 = r"\d{1,2}"
_digits_2 = r"\d{2}"

_year_group_digits_4 = named_matchgroup("year", _digits_4)
_year_group_digits_2_or_4 = named_matchgroup("year", _digits_2_or_4)
_month_group_digits_1_or_2 = named_matchgroup("month", _digits_1_or_2)
_day_group_digits_1_or_2 = named_matchgroup("day", _digits_1_or_2)

_T_or_space = any_of("T", " ")
_hour_group_digits_2 = named_matchgroup("hour", _digits_1_or_2)
_minute_group_digits_2 = named_matchgroup("minute", _digits_2)
_second_group_digits_2 = named_matchgroup("second", _digits_2)
_milliseconds_group_digits_3 = named_matchgroup("millisecond", r"\d{1,3}")
_timezone = named_matchgroup(
    "timezone", r"Z|" + non_capturing_group(r"[+\-]\d{2}:\d{2}")
)

_iso_date = (
    _year_group_digits_4
    + "-"
    + _month_group_digits_1_or_2
    + "-"
    + _day_group_digits_1_or_2
)
_iso_time = (
    _hour_group_digits_2
    + ":"
    + _minute_group_digits_2
    + optional(
        non_capturing_group(
            ":"
            + _second_group_digits_2
            + optional(non_capturing_group(r"\." + _milliseconds_group_digits_3))
        )
    )
)
_separators = (
    r"[-\s\./_;,:]+"
)

token_definitions = [
    # 1. ISO Datetime (with T or space separator) with optional seconds, milliseconds and timezone.
    # Example: 2024-02-28T14:30, 2024-02-28 14:30:00, 2024-02-28T14:30:00.123, 2024-02-28T14:30:00+02:00
    TokenDefinition(
        "Datetime",
        with_word_boundaries(_iso_date + _T_or_space + _iso_time + optional(_timezone)),
    ),
    # 2. German Date: day.month.year (e.g., 28.2.2024, 28.2. (implying current year))
    TokenDefinition(
        "Date",
        # with_word_boundaries(
        _day_group_digits_1_or_2
        + r"\."
        + _month_group_digits_1_or_2
        + r"\."
        + optional(_year_group_digits_2_or_4),
        #  ),
    ),
    # 3. ISO Date: year-month-day (e.g., 2024-02-28)
    TokenDefinition("Date", with_word_boundaries(_iso_date)),
    # 4. American Date: month/day/year (e.g., 02/28/2024)
    TokenDefinition(
        "Date",
        # with_word_boundaries(
        _month_group_digits_1_or_2
        + "/"
        + _day_group_digits_1_or_2
        + "/"
        + _year_group_digits_2_or_4,
        #  ),
    ),
    # 5. Time (only): hour:minute with optional seconds and milliseconds.
    # Examples: 14:30, 14:30:00, 14:30:00.123
    TokenDefinition(
        "Time",
        # with_word_boundaries(
        _iso_time,
        # ),
    ),
    # 6. Relative Dates in German and English.
    # Matches words like "heute", "morgen", "übermorgen", "gestern", "vorgestern" as well as
    # "today", "tomorrow", "day after tomorrow", "day before yesterday".
    # Using the inline (?i) flag to ignore case.
    TokenDefinition(
        "RelativeDate",
        r"(?i)\b(?P<rel>("
        r"heute|morgen|übermorgen|gestern|vorgestern|today|tomorrow|day after tomorrow|yesterday|day before yesterday"
        r"|(letzter |nächster |last |next )?"
        r"("
        r"montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag"
        r"|monday|tuesday|wednesday|thursday|friday|saturday|sunday"
        r"|mon|tue|wed|thu|fri|sat|sun|mo|di|mi|do|fr|sa|so"
        r")"
        r"))\b",
    ),
    TokenDefinition(
        "Pure Separators",
        _separators,
    )
]

lenient_tokenizer = get_tokenizer(token_definitions)


def main():
    print(
        # with_word_boundaries(
        _day_group_digits_1_or_2
        + r"\."
        + _month_group_digits_1_or_2
        + r"\."
        + optional(_year_group_digits_2_or_4)
        # )
    )
    while True:
        print("Input:")
        the_input = input()
        print("Tokens:")
        for token in lenient_tokenizer(the_input):
            print(token)


if __name__ == "__main__":
    main()
