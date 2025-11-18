import unittest
from datetime import datetime, date

import tzdata
from dateutil.tz import tzlocal
from dateutil.zoneinfo import gettz

from ratisbona_utils.datetime import (
    ensure_timezone,
    ensure_no_timezone,
    to_datetime,
    format_ms_HHMMSSss,
    last_day_of_month,
    month_iterator,
)
from ratisbona_utils.datetime._datetime_utils import to_next_weekday, to_last_weekday


class TestDatetimeUtils(unittest.TestCase):

    def test_ensure_timezone_must_add_tzlocal_to_datetime_without_timezone(self):
        # Given
        a_datetime = datetime(2021, 1, 1)
        # When
        result = ensure_timezone(a_datetime)
        # Then
        self.assertIsNone(a_datetime.tzinfo)
        self.assertEqual(tzlocal(), result.tzinfo)
        self.assertEqual(a_datetime.date(), result.date())
        self.assertEqual(a_datetime.time(), result.time())

    def test_ensure_timezone_must_leave_timezone_alone_if_given_already(self):
        # Given
        timezone_utc = gettz("UTC")
        a_datetime = datetime(2021, 1, 1, tzinfo=timezone_utc)

        # When
        result = ensure_timezone(a_datetime)

        # Then
        self.assertEqual(timezone_utc, result.tzinfo)
        self.assertEqual(a_datetime.date(), result.date())
        self.assertEqual(a_datetime.time(), result.time())

    def test_ensure_no_timezone_must_remove_timezone_information(self):
        # Given
        timezone_utc = gettz("UTC")
        a_datetime = datetime(2021, 1, 1, tzinfo=timezone_utc)

        # When
        result = ensure_no_timezone(a_datetime)

        # Then
        self.assertIsNone(result.tzinfo)
        self.assertEqual(a_datetime.date(), result.date())
        self.assertEqual(a_datetime.time(), result.time())

    def test_ensure_no_timezone_must_leave_datetime_without_timezone_alone(self):
        # Given
        a_datetime = datetime(2021, 1, 1)

        # When
        result = ensure_no_timezone(a_datetime)

        # Then
        self.assertIsNone(result.tzinfo)
        self.assertEqual(a_datetime.date(), result.date())
        self.assertEqual(a_datetime.time(), result.time())

    def test_to_datetime_must_convert_date_to_datetime_at_start_of_day(self):
        # Given
        a_date = date(2021, 1, 1)

        # When
        result = to_datetime(a_date)

        # Then
        self.assertEqual(
            datetime(2021, 1, 1, hour=0, minute=0, second=0, microsecond=0), result
        )

    def create_testoutput(self, show_msec: bool = True) -> str:
        # Given
        milliseconds = 12
        milliseconds = milliseconds * 60 + 34
        milliseconds = milliseconds * 60 + 56
        milliseconds = milliseconds * 1000 + 789

        # When
        return format_ms_HHMMSSss(milliseconds, show_msec=show_msec)

    def test_format_ms_HHMMSSss_must_convert_milliseconds_to_HHMMSSss(self):

        # Then
        self.assertEqual("12:34:56.789", self.create_testoutput())

    def test_format_ms_HHMMSSss_milliseconds_to_HHMMSSs_must_suppress_ms_on_show_msec_false(
        self,
    ):
        self.assertEqual("12:34:56", self.create_testoutput(show_msec=False))

    ldom = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def test_last_day_of_month_must_return_last_day_of_month(self):
        # Given
        for month, days in enumerate(self.ldom, start=1):
            # When
            result = last_day_of_month(date(2021, month, 1))

            # Then
            self.assertEqual(date(2021, month, days), result)

    def test_last_day_of_month_must_return_last_day_of_month_also_in_leap_year(self):
        for month, days in enumerate(self.ldom, start=1):
            # When
            result = last_day_of_month(date(2020, month, 1))

            if month == 2:
                # Then
                self.assertEqual(date(2020, month, 29), result)
            else:
                # Then
                self.assertEqual(date(2020, month, days), result)

    def test_month_iterator_must_provide_correct_months(self):
        # Given
        start = date(2019, 1, 31)
        end = date(2023, 12, 31)

        # When
        result = list(month_iterator(start, end))

        # Then
        expected = [
            (2019, 1),
            (2019, 2),
            (2019, 3),
            (2019, 4),
            (2019, 5),
            (2019, 6),
            (2019, 7),
            (2019, 8),
            (2019, 9),
            (2019, 10),
            (2019, 11),
            (2019, 12),
            (2020, 1),
            (2020, 2),
            (2020, 3),
            (2020, 4),
            (2020, 5),
            (2020, 6),
            (2020, 7),
            (2020, 8),
            (2020, 9),
            (2020, 10),
            (2020, 11),
            (2020, 12),
            (2021, 1),
            (2021, 2),
            (2021, 3),
            (2021, 4),
            (2021, 5),
            (2021, 6),
            (2021, 7),
            (2021, 8),
            (2021, 9),
            (2021, 10),
            (2021, 11),
            (2021, 12),
            (2022, 1),
            (2022, 2),
            (2022, 3),
            (2022, 4),
            (2022, 5),
            (2022, 6),
            (2022, 7),
            (2022, 8),
            (2022, 9),
            (2022, 10),
            (2022, 11),
            (2022, 12),
            (2023, 1),
            (2023, 2),
            (2023, 3),
            (2023, 4),
            (2023, 5),
            (2023, 6),
            (2023, 7),
            (2023, 8),
            (2023, 9),
            (2023, 10),
            (2023, 11),
            (2023, 12),
        ]
        self.assertEqual(expected, result)

    def test_to_next_weekday_must_return_next_weekday(self):
        tests = [
            (2020, 12, 31, 3, 0),  # 31.12.2020 is a Thursday
            (2020, 12, 31, 4, 1),
            (2020, 12, 31, 5, 2),
            (2020, 12, 31, 6, 3),
            (2020, 12, 31, 0, 4),
            (2020, 12, 31, 1, 5),
            (2020, 12, 31, 2, 6),
            (2021, 1, 1, 4, 0),  # 1.1.2021 is a Friday
            (2021, 1, 1, 5, 1),
            (2021, 1, 1, 6, 2),
            (2021, 1, 1, 0, 3),
            (2021, 1, 1, 1, 4),
            (2021, 1, 1, 2, 5),
            (2021, 1, 1, 3, 6),
        ]
        for year, month, day, weekday, expected in tests:
            with self.subTest(
                f"Testing {year}-{month:02d}-{day:02d} for weekday {weekday} expecting {expected} days to next weekday"
            ):
                # Given
                a_date = date(year, month, day)

                # When
                result = to_next_weekday(a_date, weekday)

                # Then
                self.assertEqual(weekday, (a_date + result).weekday())
                self.assertEqual(expected, result.days)

    def test_to_last_weekday_must_return_last_weekday(self):
        tests = [
            (2020, 12, 31, 3, 0),  # 31.12.2020 is a Thursday
            (2020, 12, 31, 4, -6),
            (2020, 12, 31, 5, -5),
            (2020, 12, 31, 6, -4),
            (2020, 12, 31, 0, -3),
            (2020, 12, 31, 1, -2),
            (2020, 12, 31, 2, -1),
            (2021, 1, 1, 4, 0),  # 1.1.2021 is a Friday
            (2021, 1, 1, 5, -6),
            (2021, 1, 1, 6, -5),
            (2021, 1, 1, 0, -4),
            (2021, 1, 1, 1, -3),
            (2021, 1, 1, 2, -2),
            (2021, 1, 1, 3, -1),

        ]
        for year, month, day, weekday, expected in tests:
            with self.subTest(
                f"Testing {year}-{month:02d}-{day:02d} for weekday {weekday} expecting {expected} days to last weekday"
            ):
                # Given
                a_date = date(year, month, day)

                # When
                result = to_last_weekday(a_date, weekday)

                # Then
                self.assertEqual(weekday, (a_date + result).weekday())
                self.assertEqual(expected, result.days)