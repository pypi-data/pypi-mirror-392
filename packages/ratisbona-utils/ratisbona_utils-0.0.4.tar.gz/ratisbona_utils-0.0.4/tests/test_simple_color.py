import unittest

from ratisbona_utils.colors.simple_color import f_inv, f, lms_color_to_uxyz_color, uxyz_color_to_lms_color


class SimpleColorTests(unittest.TestCase):

    def test_uxyz_color_to_lms_must_be_inverse(self):
        random_xyz_tuples = [
            (0.1, 0.2, 0.3),
            (0.4, 0.5, 0.6),
            (0.7, 0.8, 0.9),
            (0.1, 0.2, 0.3),
            (0.4, 0.5, 0.6),
            (0.7, 0.8, 0.9),
            (0.1, 0.2, 0.3),
            (0.4, 0.5, 0.6),
            (0.7, 0.8, 0.9),
            (0.1, 0.2, 0.3),
        ]
        for random_tuple in random_xyz_tuples:
            with self.subTest(f"Testing {random_tuple}"):
                x, y, z = lms_color_to_uxyz_color(random_tuple)
                l, m, s = uxyz_color_to_lms_color((x, y, z))
                self.assertAlmostEqual(l, random_tuple[0])

    def test_finv_must_be_inv_of_f(self):
        t=0.0
        while t<100.0:
            fval = f(t)
            finvval = f_inv(fval)
            print(t, fval, finvval)
            self.assertAlmostEqual( t, finvval)
            t += 0.01


if __name__ == '__main__':
    unittest.main()
