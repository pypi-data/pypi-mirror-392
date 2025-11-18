from datetime import date, datetime, time
from unittest import TestCase

from ratisbona_utils.datetime import lenient_tokenizer, leniently_parse, ensure_datetime
from ratisbona_utils.functional import Provider


class TestDateParser(TestCase):

    def do_parse(self, text, now_provider: Provider[datetime] = datetime.now):
        tokens = list(lenient_tokenizer(text))
        for token in tokens:
            print(token)
        result = leniently_parse(tokens, base_date_for_implicit_dates=now_provider)
        print(result)
        return result

    def test_date_parser_must_parse_valid_isodate(self):
        self.assertEqual(date(1979, 7, 18), self.do_parse("1979-07-18")[0])

    def test_date_parser_must_parse_valid_german_date(self):
        self.assertEqual(date(1979, 7, 18), self.do_parse("18.07.1979")[0])

    def test_date_parser_must_parse_valid_american_date(self):
        self.assertEqual(date(1979, 7, 18), self.do_parse("07/18/1979")[0])

    def test_date_parser_must_leniently_parse_valid_isodate_month(self):
        self.assertEqual(date(1979, 7, 1), self.do_parse("1979-7-01")[0])

    def test_date_parser_must_leniently_parse_valid_germandate_month(self):
        self.assertEqual(date(1979, 7, 18), self.do_parse("18.7.1979")[0])

    def test_date_parser_must_leniently_parse_valid_american_date_month(self):
        self.assertEqual(date(1979, 7, 18), self.do_parse("7/18/1979")[0])

    def test_date_parser_must_leniently_parse_valid_isodate_day(self):
        self.assertEqual(date(1979, 7, 1), self.do_parse("1979-07-1")[0])

    def test_date_parser_must_leniently_parse_valid_germandate_day(self):
        self.assertEqual(date(1979, 7, 1), self.do_parse("1.07.1979")[0])

    def test_date_parser_must_leniently_parse_valid_american_date_day(self):
        self.assertEqual(date(1979, 7, 1), self.do_parse("07/1/1979")[0])

    def test_date_parser_must_not_leniently_parse_isoday_year(self):
        self.assertFalse(self.do_parse("79-07-18")[0])

    def test_date_parser_must_leniently_parse_germandate_year_taking_century_from_now_provider(
        self,
    ):
        self.assertEqual(
            date(2025, 7, 18),
            self.do_parse(
                "18.07.25", now_provider=lambda: datetime(2025, 1, 1, 0, 0)
            )[0],
        )
        self.assertEqual(
            date(1925, 7, 18),
            self.do_parse(
                "18.07.25", now_provider=lambda: datetime(1926, 1, 1, 0, 0)
            )[0],
        )

    def test_date_parser_must_leniently_parse_germandate_year_taking_century_from_now_provider_using_previous_century_if_in_future(
        self,
    ):
        self.assertEqual(
            date(1925, 7, 18),
            self.do_parse("18.07.25", now_provider=lambda: datetime(2024, 1, 1, 0, 0))[0],
        )
        self.assertEqual(
            date(1825, 7, 18),
            self.do_parse("18.07.25", now_provider=lambda: datetime(1924, 1, 1, 0, 0))[0],
        )

    def test_date_parser_must_leniently_parse_german_date_without_year_taking_year_from_now_provider(self):
        self.assertEqual(
            date(2025, 7, 18),
            self.do_parse("18.07.", now_provider=lambda: datetime(2025, 1, 1, 0, 0))[0],
        )
        self.assertEqual(
            date(1925, 7, 18),
            self.do_parse("18.07.", now_provider=lambda: datetime(1925, 1, 1, 0, 0))[0],
        )

    def test_date_parser_must_leniently_parse_american_date_year(self):
        self.assertEqual(
            date(2025, 7, 18),
            self.do_parse(
                "07/18/25", now_provider=lambda: datetime(2025, 1, 1, 0, 0)
            )[0],
        )
        self.assertEqual(
            date(1925, 7, 18),
            self.do_parse(
                "07/18/25", now_provider=lambda: datetime(1926, 1, 1, 0, 0)
            )[0],
        )


    def test_date_parser_must_not_accept_illegal_day_isoformat(self):
        self.assertFalse(self.do_parse("1979-07-32")[0])
        self.assertFalse(self.do_parse("1979-02-29")[0])

    def test_date_parser_must_not_accept_illegal_day_germandate(self):
        self.assertFalse(self.do_parse("32.07.1979")[0])
        self.assertFalse(self.do_parse("29.02.1979")[0])

    def test_date_parser_must_not_accept_illegal_day_american_date(self):
        self.assertFalse(self.do_parse("07/32/1979")[0])
        self.assertFalse(self.do_parse("02/29/1979")[0])

    def test_date_parser_must_not_accept_illegal_month_isoformat(self):
        self.assertFalse(self.do_parse("1979-13-18")[0])

    def test_date_parser_must_not_accept_illegal_month_germandate(self):
        self.assertFalse(self.do_parse("18.13.1979")[0])

    def test_date_parser_must_not_accept_illegal_month_american_date(self):
        self.assertFalse(self.do_parse("13/18/1979")[0])

    def test_date_parser_must_accept_leap_year_isoformat(self):
        self.assertEqual(date(2000, 2, 29), self.do_parse("2000-02-29")[0])

    def test_date_parser_must_accept_leap_year_germandate(self):
        self.assertEqual(date(2000, 2, 29), self.do_parse("29.02.2000")[0])

    def test_date_parser_must_accept_leap_year_american_date(self):
        self.assertEqual(date(2000, 2, 29), self.do_parse("02/29/2000")[0])

    def test_date_parser_must_not_accept_non_leap_year_isoformat(self):
        self.assertFalse(self.do_parse("1900-02-29")[0])

    def test_date_parser_must_not_accept_non_leap_year_germandate(self):
        self.assertFalse(self.do_parse("29.02.1900")[0])

    def test_date_parser_must_not_accept_non_leap_year_american_date(self):
        self.assertFalse(self.do_parse("02/29/1900")[0])

    def test_date_parser_must_not_accept_stuff_before_iso_date(self):
        self.assertFalse(self.do_parse("The date is 2020-02-29")[0])

    def test_date_parser_must_not_accept_stuff_before_germandate(self):
        self.assertFalse(
            self.do_parse("Das heutige Datum ist: 29.02.2020")[0],
        )

    def test_date_parser_must_not_accept_stuff_before_american_date(self):
        self.assertFalse(
            self.do_parse("The date is 02/29/2020")[0]
        )

    def test_date_parser_must_accept_stuff_after_iso_date(self):
        self.assertEqual(
            date(2020, 2, 29), self.do_parse("2020-02-29 is the date")[0]
        )

    def test_date_parser_must_accept_stuff_after_germandate(self):
        self.assertEqual(
            date(2020, 2, 29),
            self.do_parse(
                "29.02.2020, der Tag den es eigentlich nicht geben durfte"
            )[0],
        )

    def test_date_parser_must_accept_stuff_after_american_date(self):
        self.assertEqual(
            date(2020, 2, 29), self.do_parse("02/29/2020 is the date")[0]
        )

    def test_date_parser_must_not_match_additional_numbers_before_iso_date(self):
        self.assertFalse(self.do_parse("02020-02-29")[0])

    def test_date_parser_must_not_match_additional_numbers_before_germandate(self):
        self.assertFalse(self.do_parse("02020-02-29")[0])

    def test_date_parser_must_not_match_additional_numbers_before_american_date(self):
        self.assertFalse(self.do_parse("02020-02-29")[0])

    def test_date_parser_must_not_accept_additional_numbers_after_iso_date(self):
        self.assertFalse(self.do_parse("2020-02-290")[0])

    def test_date_parser_must_not_accept_additional_numbers_after_germandate(self):
        self.assertFalse(
            self.do_parse("29.02.200", now_provider=lambda: datetime(2025, 1, 1, 0, 0))[0],
        )

    def test_date_parser_must_not_accept_additional_numbers_after_american_date(self):
        self.assertFalse(self.do_parse("02/29/200")[0])

    def test_date_parser_must_accept_iso_datetime(self):
        self.assertEqual(
            datetime(2020, 2, 29, 12, 34, 56),
            self.do_parse("2020-02-29T12:34:56")[0],
        )

    def test_date_parser_must_accept_iso_datetime_with_microseconds(self):
        self.assertEqual(
            datetime(2020, 2, 29, 12, 34, 56, 789000),
            self.do_parse("2020-02-29T12:34:56.789")[0],
        )

    def test_date_parser_must_ignore_trailing_numbers_in_iso_datetime(self):
        self.assertEquals(
            datetime(2020, 2, 29, 12, 34, 56),
            self.do_parse("2020-02-29T12:34:56.789123")[0],
        )

    def test_date_parser_must_not_match_leading_numbers_in_datetime(self):
        self.assertFalse(self.do_parse("1232020-02-29T12:34:56.789123")[0])

    def test_date_parser_must_accept_iso_datetime_even_without_seconds(self):
        self.assertEqual(
            datetime(2020, 2, 29, 12, 34),
            self.do_parse("2020-02-29T12:34")[0],
        )

    def test_date_parser_must_accept_time_with_hour_and_minutes(self):
        self.assertEqual(
            time(12, 34),
            self.do_parse("12:34")[0],
        )

    def test_date_parser_must_accept_time_with_hour_parsed_leniently(self):
        self.assertEqual(
            time(8, 34),
            self.do_parse("8:34")[0]
        )

    def test_date_parser_must_not_leniently_parse_minutes(self):
        self.assertFalse(self.do_parse("12:4")[0])

    def test_date_parser_must_accept_time_with_hour_and_seconds(self):
        self.assertEqual(
            time(12, 34, 56),
            self.do_parse("12:34:56")[0],
        )

    def test_date_parser_must_not_leniently_parse_seconds(self):
        result, tokens = self.do_parse("12:34:5")
        self.assertEqual(time(12, 34), result)
        self.assertEqual(1, len(tokens))
        self.assertEqual("Text", tokens[0].token_type_name)

    def test_ensure_datetime_must_return_datetime_on_datetime_given(self):
        self.assertEqual(
            datetime(2020, 2, 29, 12, 34),
            ensure_datetime(datetime(2020, 2, 29, 12, 34))
        )

    def test_ensure_datetime_must_return_datetime_with_min_time_on_date_given(self):
        self.assertEqual(
            datetime(2020, 2, 29, 0, 0),
            ensure_datetime(date(2020, 2, 29))
        )

    def test_ensure_datetime_must_return_datetime_with_date_taken_from_nowprovider_on_time_given(self):
        self.assertEqual(
            datetime(2020, 2, 29, 13, 47),
            ensure_datetime(time(13,47), now_provider=lambda: datetime(2020, 2, 29, 1, 34))
        )


