from pathlib import Path
from unittest import TestCase

from ratisbona_utils.io.file_iterator import FileIterable


class TestFileIo(TestCase):

    def test_read_file(self):
        with open(Path(__file__)) as f:
            expected_content = f.read().splitlines()

        actual_content = list(FileIterable(Path(__file__)))
        print(actual_content)
        self.assertEqual(expected_content, actual_content)

    def test_read_file_using_next(self):
        with open(Path(__file__)) as f:
            expected_content = f.read().splitlines()

        iterator = iter(FileIterable(Path(__file__)))
        while True:
            try:
                actual_content = next(iterator)
                self.assertEqual(expected_content.pop(0), actual_content)
            except StopIteration:
                break
        self.assertEqual(len(expected_content), 0)