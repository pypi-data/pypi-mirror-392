import unittest


class LatexTestCase(unittest.TestCase):
    def test_make_text_to_latex_paragraphs_must_emit_paragraphs(self):
        from ratisbona_utils.latex.linebreaks import make_text_to_latex_paragraphs

        input_text = "Hello!\nTest!\nThis is a test.\n\nThis is another paragraph.\n\n\nThis is yet another paragraph."
        expected_output = "Hello!\n\nTest!\n\nThis is a test.\n\nThis is another paragraph.\n\nThis is yet another paragraph.\n"
        actual_output = make_text_to_latex_paragraphs(input_text)
        self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()
