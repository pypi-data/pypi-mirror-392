from unittest import TestCase

import unittest

from ratisbona_utils.languages import encode_english_short_ordinal


class TestEnglish(TestCase):

    def test_encode_english_short_ordinal_must_provide_ith_for_most_numbers(self):
        for i in range(44, 51, 1200):
            self.assertEqual(encode_english_short_ordinal(i), f"{i}th")

    def test_encode_english_short_ordinal_must_append_st_for_1_21_31(self):
        for i in [1, 21, 31, 41, 51, 61, 71, 81, 91, 101, 121, 131]:
            self.assertEqual(encode_english_short_ordinal(i), f"{i}st")

    def test_encode_short_orginal_must_append_th_for_11_111_211(self):
        for i in [11, 111, 211, 311, 411, 511, 611, 711, 811, 911]:
            self.assertEqual(encode_english_short_ordinal(i), f"{i}th")

    def test_encode_short_orginal_must_append_nd_for_2_22_32_42_(self):
        for i in [2, 22, 32, 42, 52, 62, 72, 82, 92, 102, 122, 132]:
            self.assertEqual(encode_english_short_ordinal(i), f"{i}nd")

    def test_encode_short_orginal_must_append_th_for_12_112_212_312_(self):
        for i in [12, 112, 212, 312, 412, 512, 612, 712, 812, 912, 1012, 1112, 1212, 1312]:
            self.assertEqual(encode_english_short_ordinal(i), f"{i}th")

    def test_encode_short_orginal_must_append_rd_for_3_33_43_53_63_73_83_93_103_123(self):
        for i in [3, 33, 43, 53, 63, 73, 83, 93, 103, 123, 133]:
            self.assertEqual(encode_english_short_ordinal(i), f"{i}rd")

    def test_encode_short_orginal_must_append_th_for_13_113_213_313_413_513_1013_1113(self):
        for i in [13, 113, 213, 313, 413, 513, 1013, 1113, 1213, 1313]:
            self.assertEqual(encode_english_short_ordinal(i), f"{i}th")


if __name__ == '__main__':
    unittest.main()
