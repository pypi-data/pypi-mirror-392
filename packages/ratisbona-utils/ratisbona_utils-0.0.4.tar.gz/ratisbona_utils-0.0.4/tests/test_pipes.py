from pathlib import Path
from unittest import TestCase

from ratisbona_utils.pipes import cat, collect, fcat


class TestPipes(TestCase):

    def test_cat(self):
        result = cat(range(0, 10)) | (lambda x: x * 2) | (lambda x: x + 1) | collect(list)
        print(result)
        self.assertEqual(result, [1, 3, 5, 7, 9, 11, 13, 15, 17, 19])

    def test_fcat(self):
        result = fcat(Path(__file__)) | (lambda x: f'-->{x}<--') | collect(list)
        print(result)

        with open(Path(__file__)) as f:
            expected_content = ['-->' + x + '<--' for x in f.read().splitlines()]

        self.assertEqual(result, expected_content)
