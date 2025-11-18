import unittest

from ratisbona_utils.arrays import D2Array, d2array_to_separated


def generate_test_array():
    return D2Array.by_generating_func(lambda r, c: (r, c), 9, 5)

class D2ArraySerdeTestCase(unittest.TestCase):

    def test_serializing_must_yield_separated_values(self):
        array = generate_test_array()
        serialized = d2array_to_separated(array, separator=';')
        exptected = ""
        for row in range(9):
            for col in range(5):
                exptected += f"({row}, {col})"
                if col < 4:
                    exptected += ';'
                else:
                    exptected += '\n'
        print("Expected result:")
        print(exptected)
        print("Actual result:")
        print(serialized)
        self.assertEqual(exptected, serialized)



if __name__ == '__main__':
    unittest.main()
