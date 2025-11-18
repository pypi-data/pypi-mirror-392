import unittest
from datetime import date

from ratisbona_utils.datetime import calculate_easter_date


class TestGausianEaster(unittest.TestCase):


    known_easter_dates=[
        date(2020, 4, 12),
        date(2021, 4, 4),
        date(2022, 4, 17),
        date(2023, 4, 9),
        date(2024, 3, 31),
        date(2025, 4, 20),
        date(2026, 4, 5),
        date(2027, 3, 28),
        date(2028, 4, 16),
        date(2029, 4, 1),
        date(2030, 4, 21),
    ]

    def test_easter_sunday_must_match_known_values(self):
        for index, year in enumerate(range(2020,2031)):
            with self.subTest(year=year):
                self.assertEqual(self.known_easter_dates[index], calculate_easter_date(year))
                print(calculate_easter_date(year))



if __name__ == '__main__':
    unittest.main()
