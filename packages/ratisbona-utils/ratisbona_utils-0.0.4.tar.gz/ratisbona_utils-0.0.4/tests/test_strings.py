import unittest

from ratisbona_utils.strings import (
    snake_to_words, words_to_camel, camel_to_words, pascal_to_words, shorten, indent
)
from ratisbona_utils.strings._alignment import si_format_number


class TestStrings(unittest.TestCase):

    def test_snake_to_words_must_yield_words(self):
        words = snake_to_words('this_is_a_test')
        self.assertEqual(words, ['this', 'is', 'a', 'test'])

    def test_words_to_camel_must_yield_camel_casing(self):
        result = words_to_camel(['this', 'is', 'a', 'test'])
        self.assertEqual('thisIsATest', result)

    def test_camel_to_words_must_yield_words_in_lowercase(self):
        result = camel_to_words('entityFactoryProviderInterface')
        self.assertEqual(['entity','factory', 'provider', 'interface'], result)

    def test_camel_to_words_must_yield_word_if_only_one_word_given(self):
        result = camel_to_words('entity')
        self.assertEqual(['entity'], result)

    def test_camel_to_words_must_complain_if_not_camel_given(self):
        with self.assertRaises(ValueError) as ve:
            camel_to_words('EntityProvider')
        self.assertTrue('camel' in str(ve.exception))
        self.assertTrue('not' in str(ve.exception))

    def test_pascal_to_words_must_yield_words_in_lowercase(self):
        result = pascal_to_words('EntityFactoryProviderInterface')
        self.assertEqual(['entity','factory', 'provider', 'interface'], result)

    def test_pascal_to_words_must_yield_word_if_only_one_word_given(self):
        result = pascal_to_words('Entity')
        self.assertEqual(['entity'], result)

    def test_camel_to_words_must_complain_if_not_pascal_given(self):
        with self.assertRaises(ValueError) as ve:
            camel_to_words('EntityProvider')
        self.assertTrue('camel' in str(ve.exception))
        self.assertTrue('not' in str(ve.exception))

    def test_pascal_to_words_must_complain_if_not_pascal_given(self):
        with self.assertRaises(ValueError) as ve:
            pascal_to_words('entityProvider')
        self.assertTrue('pascal' in str(ve.exception))
        self.assertTrue('not' in str(ve.exception))

    def test_shorten_must_return_text_if_shorter_than_max_length(self):
        result = shorten('this is a test', 20)
        self.assertEqual('this is a test', result)

    def test_shorten_must_raise_if_max_length_less_than_14(self):
        with self.assertRaises(ValueError) as ve:
            shorten('this is a test', 10)
        self.assertTrue('14' in str(ve.exception))

    def test_shorten_must_shorten(self):
        test='this is a very long test with many chars. Hello World, how are you?'
        for i in range(14, 20):
            result = shorten(test, i)
            print(result)
            self.assertTrue(len(result) == i)

    def test_elipsis_must_contain_correct_string_length(self):
        for strlen in range(20, 1000, 10):
            string = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ" * (strlen // 26 + 1))[:strlen]

            for i in range(14, 19 if strlen < 101 else 100):
                result = shorten(string, i)
                print(result)
                before, _, after = result.split("...")
                self.assertTrue(string.startswith(before))
                self.assertTrue(string.endswith(after))
                self.assertTrue(len(result) == i)
                self.assertTrue(f"[{len(string)}]" in result)

    def test_elipsis_must_contain_999plus_for_very_long_strings(self):
        string = "A" * 1000
        result = shorten(string, 14)
        print(result)
        self.assertTrue(len(result) == 14)
        self.assertTrue("[>999]" in result)

    def test_indent_must_indent(self):
        # given
        text = 'This is a test\nwith two lines'
        # when
        result = indent(text, 4)
        # then
        self.assertEqual('    This is a test\n    with two lines', result)



    def test_si_format_number_decimal(self):
        self.assertEqual(si_format_number(999, binary_units=False), '999')
        self.assertEqual(si_format_number(1000, binary_units=False), '1 k')
        self.assertEqual(si_format_number(1500, binary_units=False), '1 k')
        self.assertEqual(si_format_number(1000000, binary_units=False), '1 M')
        self.assertEqual(si_format_number(1000000000, binary_units=False), '1 G')
        self.assertEqual(si_format_number(1000000000000, binary_units=False), '1 T')

    def test_si_format_number_binary(self):
        self.assertEqual(si_format_number(1023, binary_units=True), '1023')
        self.assertEqual(si_format_number(1024, binary_units=True), '1 ki')
        self.assertEqual(si_format_number(1536, binary_units=True), '1 ki')
        self.assertEqual(si_format_number(1048576, binary_units=True), '1 Mi')
        self.assertEqual(si_format_number(1073741824, binary_units=True), '1 Gi')
        self.assertEqual(si_format_number(1099511627776, binary_units=True), '1 Ti')


if __name__ == '__main__':
    unittest.main()
