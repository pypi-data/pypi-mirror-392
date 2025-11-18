
import unittest
from pathlib import Path
from random import Random

from ratisbona_utils.functional import first
from ratisbona_utils.functional._functional import repeat_function, create_id_index, nth_element, nonordered_groupby, \
    map_all_values_of_the_dictionary
from ratisbona_utils.monads import Just


class FunctionalTestCase(unittest.TestCase):

    def test_repeat_function_must_repeat_function(self):

        # Given
        def testfunction(x, y):
            return x*2, y*3

        # Then
        result = repeat_function(testfunction, 3, 3, 2)

        # Expect
        self.assertEqual(result, (24, 54))

    def test_repeating_0_times_must_be_identity(self):

        # Given
        def testfunction(x, y):
            return x*2, y*3

        # Then
        result = repeat_function(testfunction, 0, 3, 2)

        # Expect
        self.assertEqual(result, (3, 2))

    def test_repeating_minus_times_must_yield_exception(self):

        def testfunction(x, y):
            return x*2, y*3

        with self.assertRaises(ValueError) as the_error:
            repeat_function(testfunction, -1, 1, 1)

        self.assertTrue('Impossible' in str(the_error.exception))

    def test_repeating_single_returnvalue_function_must_be_possible(self):

        # Given
        testpath = Path('A/B/C/D/E/F')

        # Then use a lambda expression that creates tuple of next arguments as return-value!
        hopefully_a = repeat_function(lambda apath: (apath.parent,), 5, testpath)

        # Expect and not that you get a tuple back from the last call.
        self.assertEqual(hopefully_a[0], testpath.parent.parent.parent.parent.parent)

    def test_first_must_provide_first_element_of_iterator(self):
        # Given...
        test_data = [1,2,3,4,5]
        iterator = iter(test_data)

        # Then
        the_first = first(iterator)

        # Expect
        self.assertEqual(the_first, Just(1))

    def test_first_must_provide_just_first_element_of_iterable(self):
        # Given...
        test_data = [1,2,3,4,5]

        # Then
        the_first = first(test_data)

        # Expect
        self.assertEqual(the_first, Just(1))

    def test_first_must_provide_Nothing_on_empty_iterator(self):
        # Given...
        test_data = []
        iterator = iter(test_data)

        # Then
        the_first = first(iterator)

        # Expect
        self.assertFalse(the_first)

    def test_first_must_provide_Nothing_on_empty_iterable(self):
        # Given...
        test_data = []

        # Then
        the_first = first(test_data)

        # Expect
        self.assertFalse(the_first)

    def test_first_must_handle_default_on_empty_iterable(self):
        # Given...
        test_data = []

        # Then
        the_first = first(test_data).default_or_throw(42)

        # Expect
        self.assertEqual(42, the_first)


    def test_id_index_must_provide_index(self):
        # Given...
        # Objects with ids in 0-th position.
        test_data = (
            (1, 'Oans'), (2, 'Zwoa'), (3, 'Dreie')
        )

        # Then...
        id_index = create_id_index(test_data, nth_element(0))

        # Expect...
        # an index that maps from id to object.
        self.assertEqual(len(id_index), 3)
        self.assertEqual(id_index[1][1], 'Oans')
        self.assertEqual(id_index[2][1], 'Zwoa')
        self.assertEqual(id_index[3][1], 'Dreie')

    def test_id_index_must_provide_empty_index_for_empty_iterable(self):
        test_data = ()
        id_index = create_id_index(test_data, nth_element(0))
        self.assertIsNotNone(id_index)
        self.assertEqual(len(id_index), 0)

    def test_nth_element_must_return_nth_element(self):
        test_data = (1, 2, 3)
        self.assertEqual(nth_element(0)(test_data), 1)
        self.assertEqual(nth_element(1)(test_data), 2)
        self.assertEqual(nth_element(2)(test_data), 3)

    def test_nonordered_groupby_must_return_grouped_results_especially_if_iterable_not_sorted(self):
        # Given..
        # Note that it's not the infamous fizzbuzz but more like fizz + buzz!
        test_data = [(i, f'Number {i}') for i in range(1,16)]
        additionals = []
        for i, number in test_data:
            if i % 3 == 0:
                additionals.append((i, 'Fizz'))
            if i % 5 == 0:
                additionals.append((i, 'Buzz'))
        test_data = test_data + additionals
        Random(42).shuffle(test_data)

        # Then...
        result = nonordered_groupby(test_data, nth_element(0))

        # Expect...
        self.assertEqual(len(result), 15)
        self.assertEqual(set(result[1]), {(1, 'Number 1')})
        self.assertEqual(set(result[2]), {(2, 'Number 2')})
        self.assertEqual(set(result[3]), {(3, 'Number 3'), (3, 'Fizz')})
        self.assertEqual(set(result[4]), {(4, 'Number 4')})
        self.assertEqual(set(result[5]), {(5, 'Number 5'), (5, 'Buzz')})
        self.assertEqual(set(result[6]), {(6, 'Number 6'), (6, 'Fizz')})
        self.assertEqual(set(result[7]), {(7, 'Number 7')})
        self.assertEqual(set(result[8]), {(8, 'Number 8')})
        self.assertEqual(set(result[9]), {(9, 'Number 9'), (9, 'Fizz')})
        self.assertEqual(set(result[10]), {(10, 'Number 10'), (10, 'Buzz')})
        self.assertEqual(set(result[11]), {(11, 'Number 11')})
        self.assertEqual(set(result[12]), {(12, 'Number 12'), (12, 'Fizz')})
        self.assertEqual(set(result[13]), {(13, 'Number 13')})
        self.assertEqual(set(result[14]), {(14, 'Number 14')})
        self.assertEqual(set(result[15]), {(15, 'Number 15'), (15, 'Fizz'), (15, 'Buzz')})

    def test_map_values_must_map_values(self):
        # Given...
        test_data = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        # Then...
        result = map_all_values_of_the_dictionary(lambda x: x * 2, test_data)

        # Expect...
        self.assertEqual(result['a'], 2)
        self.assertEqual(result['b'], 4)
        self.assertEqual(result['c'], 6)


if __name__ == '__main__':
    unittest.main()