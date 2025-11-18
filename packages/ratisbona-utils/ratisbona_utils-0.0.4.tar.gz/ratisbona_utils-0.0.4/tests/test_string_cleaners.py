import unittest

import unittest
from ratisbona_utils.strings._cleaning import (
    sclean_transliterate,
    sclean_unidecode,
    sclean_tolower,
    sclean_samba_conform,
    sclean_umlauts,
    sclean_despace,
    sclean_escape,
    sclean_parentesis,
    sclean_brackets,
    sclean_curly_brackets,
    sclean_leading_space,
    sclean_trailing_space,
    sclean_leading_dash,
    sclean_trailing_dash,
    sclean_leading_underscore,
    sclean_trailing_underscore,
    sclean_multiple_underscores,
    sclean_commas,
    sclean_exclamation_marks,
    sclean_single_quotes,
    sclean_multiple_points,
    sclean_ampers_and,
    sclean_multiple_dashes,
    sclean_multiple_underscores_dashes,
    sclean_multiple_spaces,
    sclean_dashes_before_suffix,
    string_cleaner,
    cleaners
)

class TestStringCleaning(unittest.TestCase):

    def test_sclean_transliterate(self):
        self.assertEqual(sclean_transliterate("Привет"), "Privet")

    def test_sclean_unidecode(self):
        self.assertEqual(sclean_unidecode("你好"), "Ni Hao ")

    def test_sclean_tolower(self):
        self.assertEqual(sclean_tolower("Hello World"), "hello world")

    def test_sclean_samba_conform(self):
        self.assertEqual(sclean_samba_conform("file:name"), "file_colon_name")

    def test_sclean_umlauts(self):
        self.assertEqual(sclean_umlauts("äöüÄÖÜß"), "aeoeueAeOeUess")

    def test_sclean_despace(self):
        self.assertEqual(sclean_despace("hello world"), "hello_world")

    def test_sclean_escape(self):
        self.assertEqual(sclean_escape("hello\x1bworld"), "hello_esc_world")

    def test_sclean_parentesis(self):
        self.assertEqual(sclean_parentesis("hello(world)"), "helloworld")

    def test_sclean_brackets(self):
        self.assertEqual(sclean_brackets("hello[world]"), "helloworld")

    def test_sclean_curly_brackets(self):
        self.assertEqual(sclean_curly_brackets("hello{world}"), "helloworld")

    def test_sclean_leading_space(self):
        self.assertEqual(sclean_leading_space("  hello"), "hello")

    def test_sclean_trailing_space(self):
        self.assertEqual(sclean_trailing_space("hello  "), "hello")

    def test_sclean_leading_dash(self):
        self.assertEqual(sclean_leading_dash("-hello"), "hello")

    def test_sclean_trailing_dash(self):
        self.assertEqual(sclean_trailing_dash("hello-"), "hello")

    def test_sclean_leading_underscore(self):
        self.assertEqual(sclean_leading_underscore("_hello"), "hello")

    def test_sclean_trailing_underscore(self):
        self.assertEqual(sclean_trailing_underscore("hello_"), "hello")

    def test_sclean_multiple_underscores(self):
        self.assertEqual(sclean_multiple_underscores("hello__world"), "hello_world")

    def test_sclean_commas(self):
        self.assertEqual(sclean_commas("hello,world"), "helloworld")

    def test_sclean_exclamation_marks(self):
        self.assertEqual(sclean_exclamation_marks("hello!world"), "helloworld")

    def test_sclean_single_quotes(self):
        self.assertEqual(sclean_single_quotes("hello'world"), "helloworld")

    def test_sclean_multiple_points(self):
        self.assertEqual(sclean_multiple_points("hello..world"), "hello.world")

    def test_sclean_ampers_and(self):
        self.assertEqual(sclean_ampers_and("hello&world"), "helloandworld")

    def test_sclean_multiple_dashes(self):
        self.assertEqual(sclean_multiple_dashes("hello--world"), "hello-world")

    def test_sclean_multiple_underscores_dashes(self):
        self.assertEqual(sclean_multiple_underscores_dashes("hello_-_world"), "hello_-_world")

    def test_sclean_multiple_spaces(self):
        self.assertEqual(sclean_multiple_spaces("hello  world"), "hello world")

    def test_sclean_dashes_before_suffix(self):
        self.assertEqual(sclean_dashes_before_suffix("hello- .txt"), "hello.txt")

    def test_string_cleaner(self):
        self.assertEqual(string_cleaner("Hello, World!", ["tolower", "commas", "exclamation_marks"]), "hello world")

if __name__ == "__main__":
    unittest.main()