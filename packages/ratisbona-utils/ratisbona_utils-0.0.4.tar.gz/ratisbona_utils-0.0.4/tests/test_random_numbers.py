import unittest

from ratisbona_utils.random_numbers import lsfr_B4BCD35C_32Bit


class MyTestCase(unittest.TestCase):


    def test_lsfr_B4BCD35C_32Bit_must_yield_known_numbers(self):
        """
        Test that the lsfr_B4BCD35C_32Bit must yield known numbers from

        https://www.analog.com/en/resources/design-notes/random-number-generation-using-lfsr.html

        """
        random = lsfr_B4BCD35C_32Bit(0xB4BCD35C)

        numbers = [next(random) for _ in range(4)]

        hex_numbers = [hex(number) for number in numbers]

        self.assertEqual(['0x5a5e69ae', '0x2d2f34d7', '0xa22b4937', '0xe5a977c7'], hex_numbers)

    # Will run more than 10 Minutes!
    def donttest_period_lsfr_B4BCD35C_32Bit_must_be_2pow32(self):
        """
        Test that the lsfr_B4BCD35C_32Bit must yield known numbers from

        https://www.analog.com/en/resources/design-notes/random-number-generation-using-lfsr.html

        """
        random = lsfr_B4BCD35C_32Bit(0xB4BCD35C)

        first_number = next(random)
        period = 1
        while True:
            number = next(random)
            if number == first_number:
                break
            period += 1
            if period % 1_000_000 == 0:
                print(f"{period:_}")
        self.assertEqual(2**32-1, period)

if __name__ == '__main__':
    unittest.main()
