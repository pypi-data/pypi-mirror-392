from unittest import TestCase, main

from ratisbona_utils.boxdrawing import draw_box, LineStyle


class TestBoxDrawing(TestCase):

    def test_draw_box_should_draw_box(self):
        # Given
        multiline_text = """There was a yound lady from Riga,
Who rode with a smile on a tiger.
They returned from the ride
With the lady inside,
And the smile on the face of the tiger."""
        # When
        result = draw_box(multiline_text, LineStyle.SINGLE)

        # Then
        expect="""┌─────────────────────────────────────────┐
│ There was a yound lady from Riga,       │
│ Who rode with a smile on a tiger.       │
│ They returned from the ride             │
│ With the lady inside,                   │
│ And the smile on the face of the tiger. │
└─────────────────────────────────────────┘
"""
        self.assertEqual(expect, result)


    def test_draw_box_should_draw_double_box(self):
        # Given
        multiline_text = """There was a yound lady from Riga,
Who rode with a smile on a tiger.
They returned from the ride
With the lady inside,
And the smile on the face of the tiger."""
        # When
        result = draw_box(multiline_text, LineStyle.DOUBLE)

        # Then
        expect = """╔═════════════════════════════════════════╗
║ There was a yound lady from Riga,       ║
║ Who rode with a smile on a tiger.       ║
║ They returned from the ride             ║
║ With the lady inside,                   ║
║ And the smile on the face of the tiger. ║
╚═════════════════════════════════════════╝
"""
        self.assertEqual(expect, result)



if __name__ == "__main__":
    main()
