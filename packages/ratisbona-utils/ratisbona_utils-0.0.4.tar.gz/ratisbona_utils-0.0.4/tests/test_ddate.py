import unittest
from datetime import timedelta, date
from multiprocessing import process

import asyncio
from contourpy.util.data import simple
from ratisbona_utils.asyncio import simple_run_command
from ratisbona_utils.datetime import yold_by_date, maybe_get_discordian_season_and_day, maybe_get_discordian_weekday, \
    decode, ddate


class TestDDate(unittest.TestCase):#

    def test_redate_must_be_same_as_translated_date(self):
        for day in range(0, 800):
            a_date = date(2024, 1, 1) + timedelta(days=day)
            yold = yold_by_date(a_date)
            season, day = maybe_get_discordian_season_and_day(a_date)
            weekday = maybe_get_discordian_weekday(a_date)
            redate = decode(day, season, yold)
            self.assertEqual(a_date, redate)

    def test_ddate_must_be_equal_to_cmd_line_tool(self):
        for day in range(0,800):
            # given
            a_date = date(2024, 1, 1) + timedelta(days=day)
            yold = yold_by_date(a_date)
            season, dday = maybe_get_discordian_season_and_day(a_date)
            weekday = maybe_get_discordian_weekday(a_date)

            # when
            string = ddate(dday, season, weekday, yold)


            # then
            # shell invokde ddate
            cmd = f'ddate +"Today is %{{%A, the %e of %B%}} in the YOLD %Y" {a_date.strftime("%d %m %Y")}'
            retval, stdout, stderr = asyncio.run(simple_run_command(cmd))
            print(a_date, season, dday, string, stdout)
            self.assertEqual(stdout.strip(), string)




if __name__ == '__main__':
    unittest.main()
