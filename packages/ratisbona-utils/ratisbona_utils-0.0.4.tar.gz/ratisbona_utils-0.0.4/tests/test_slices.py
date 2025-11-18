import unittest
from ratisbona_utils.arrays._slices import slice_2d_recognition, slice_parsing

class SlicesTestCase(unittest.TestCase):

    def test_recognize_slices_must_allow_single_slice(self):
        rowslice, colslice = slice_2d_recognition(slice(2, 5))
        self.assertEqual(rowslice, slice(2, 5))
        self.assertIsNone(colslice)

    def test_recognize_slices_must_allow_tuple_of_slices(self):
        rowslice, colslice = slice_2d_recognition((slice(1, 4), slice(2, 6)))
        self.assertEqual(rowslice, slice(1, 4))
        self.assertEqual(colslice, slice(2, 6))

    def test_recognize_slices_must_raise_value_error_on_invalid_tuple_length(self):
        with self.assertRaises(ValueError) as cm:
            _ = slice_2d_recognition((slice(0, 5), slice(0, 5), slice(0, 5)))
        print(cm.exception)

    def test_recognize_slices_must_allow_single_integer(self):
        rowslice, colslice = slice_2d_recognition(3)
        self.assertEqual(rowslice, 3)
        self.assertIsNone(colslice)

    def test_recognize_slices_must_allow_tuple_of_integer_and_slice(self):
        rowslice, colslice = slice_2d_recognition((4, slice(1, 5)))
        self.assertEqual(rowslice, 4)
        self.assertEqual(colslice, slice(1, 5))

    def test_recognize_slices_must_allow_tuple_of_slice_and_integer(self):
        rowslice, colslice = slice_2d_recognition((slice(0, 3), 2))
        self.assertEqual(rowslice, slice(0, 3))
        self.assertEqual(colslice, 2)

    def test_regonize_slices_must_allow_tuple_of_integers(self):
        rowslice, colslice = slice_2d_recognition((1, 3))
        self.assertEqual(rowslice, 1)
        self.assertEqual(colslice, 3)

    def test_parse_slices_must_handle_slice_correctly(self):
        start, end, step = slice_parsing(slice(2, 8, 3), 10)
        self.assertEqual((start, end, step), (2, 8, 3))

    def test_parse_slices_must_handle_integer_correctly(self):
        start, end, step = slice_parsing(5, 10)
        self.assertEqual((start, end, step), (5, 6, 1))

    def test_parse_slices_must_handle_slice_with_none_values(self):
        start, end, step = slice_parsing(slice(None, None, None), 10)
        self.assertEqual((start, end, step), (0, 10, 1))

    def test_parse_slices_must_raise_value_error_on_invalid_type(self):
        with self.assertRaises(ValueError) as cm:
            _ = slice_parsing("invalid", 10)
        print(cm.exception)

    def test_parse_slices_must_handle_none_as_full_range(self):
        start, end, step = slice_parsing(None, 10)
        self.assertEqual((start, end, step), (0, 10, 1))




if __name__ == '__main__':
    unittest.main()
