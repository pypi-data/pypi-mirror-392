import unittest

from ratisbona_utils.arrays import D2Array



def generate_test_array():
    return D2Array.by_generating_func(lambda r, c: (r, c), 9, 5)


class D2ArrayTestCase(unittest.TestCase):

    def test_iterator_must_traverse_array_in_row_major_order(self):
        the_test_array = generate_test_array()
        expected_cells = []
        for row in range(9):
            for col in range(5):
                expected_cells.append((row, col))
        actual_cells = list(the_test_array)
        self.assertEqual(expected_cells, actual_cells)

    def test_slicing_must_produce_correct_subarray(self):
        the_test_array = generate_test_array()
        subarray = the_test_array[2:7:2, 1:5:2]
        expected_cells = []
        for row in range(2, 7, 2):
            for col in range(1, 5, 2):
                expected_cells.append((row, col))
        actual_cells = list(subarray)
        self.assertEqual(expected_cells, actual_cells)

    def test_slicing_must_allow_element_access(self):
        the_test_array = generate_test_array()
        for row in range(9):
            for col in range(5):
                expected = (row, col)
                actual = next(iter(the_test_array[row, col]))
                print(f"Checking [{row}, {col}]: {actual}")
                self.assertEqual(expected, actual)

    def test_slicing_must_raise_value_error_on_invalid_slices(self):
        the_test_array = generate_test_array()
        with self.assertRaises(ValueError) as cm:
            _ = the_test_array[0:0, 0:5]
        print(cm.exception)

    def test_slicing_must_raise_value_error_on_invalid_slice_types(self):
        the_test_array = generate_test_array()
        with self.assertRaises(ValueError) as cm:
            _ = the_test_array["invalid", 0:5]
        print(cm.exception)
        with self.assertRaises(ValueError) as cm:
            _ = the_test_array[0:5, "invalid"]
        print(cm.exception)

    def test_slicing_must_raise_value_error_on_invalid_tuple_length(self):
        the_test_array = generate_test_array()
        with self.assertRaises(ValueError) as cm:
            _ = the_test_array[0:5, 0:5, 0:5]
        print(cm.exception)

    def test_slicing_single_row_and_column(self):
        the_test_array = generate_test_array()
        subarray = the_test_array[4]
        expected_cells = []
        for col in range(5):
            expected_cells.append((4, col))
        actual_cells = list(subarray)
        self.assertEqual(expected_cells, actual_cells)

    def test_slicing_must_clone_array(self):
        the_test_array = generate_test_array()
        subarray = the_test_array[:, :]
        expected_cells = list(the_test_array)
        actual_cells = list(subarray)
        self.assertEqual(expected_cells, actual_cells)


    def test_diagonal_iterator(self):
        the_test_array = generate_test_array()
        diagonal_elements = list(the_test_array.diagonal_iterator())
        expected_elements = [(i, i) for i in range(min(the_test_array.num_rows, the_test_array.num_cols))]
        self.assertEqual(expected_elements, diagonal_elements)

    def test_diagonal_numbers(self):
        the_test_array = generate_test_array() # 9 rows, 5 cols

        min_diagonal_index = -(the_test_array.num_rows - 1)
        max_diagonal_index = the_test_array.num_cols - 1

        self.assertEqual(-8, min_diagonal_index)
        self.assertEqual(4, max_diagonal_index)

    def test_lower_diagonals_without_wrapping(self):
        the_test_array = generate_test_array()
        for diag_index in range(-8, 0):
            expected_elements = []
            row_start = max(0, -diag_index)
            col_start = 0
            while row_start < the_test_array.num_rows and col_start < the_test_array.num_cols:
                expected_elements.append((row_start, col_start))
                row_start += 1
                col_start += 1
            actual_elements = list(the_test_array.diagonal_iterator(diag_index, wrap_around=False))
            self.assertEqual(expected_elements, actual_elements)

    def test_upper_diagonals_without_wrapping(self):
        the_test_array = generate_test_array()
        for diag_index in range(1, 5):
            expected_elements = []
            row_start = 0
            col_start = diag_index
            while row_start < the_test_array.num_rows and col_start < the_test_array.num_cols:
                expected_elements.append((row_start, col_start))
                row_start += 1
                col_start += 1
            actual_elements = list(the_test_array.diagonal_iterator(diag_index, wrap_around=False))
            self.assertEqual(expected_elements, actual_elements)

    def test_lower_diagonals_with_wrapping(self):
        the_test_array = generate_test_array()
        for diag_index in range(-8, 0):
            expected_elements = []
            row_start = max(0, -diag_index)
            col_start = 0
            while len(expected_elements) < the_test_array.num_rows:
                expected_elements.append((row_start % the_test_array.num_rows, col_start % the_test_array.num_cols))
                row_start += 1
                col_start += 1
            actual_elements = list(the_test_array.diagonal_iterator(diag_index, wrap_around=True))
            print(f"Diagonal {diag_index} with wrapping: expected \n{expected_elements}, got \n{actual_elements}")
            self.assertEqual(expected_elements, actual_elements)







if __name__ == '__main__':
    unittest.main()
