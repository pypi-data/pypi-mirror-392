import unittest

from ratisbona_utils.nonbraindead_enums import ObjectEnum

class PredefinedNamedColors(ObjectEnum):
    FULL_RED = {"colorname": "full red", "red": 255, "green": 0, "blue": 0}
    FULL_GREEN = {"colorname": "full green", "red": 0, "green": 255, "blue": 0}
    FULL_BLUE = {"colorname": "full blue", "red": 0, "green": 0, "blue": 255}

    def getHexString(self) -> str:
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"


class ObjectEnumTestcase(unittest.TestCase):
    def test_enum_members(self):
        self.assertEqual(3, len(PredefinedNamedColors))
        self.assertIn(PredefinedNamedColors.FULL_RED, PredefinedNamedColors)
        self.assertIn(PredefinedNamedColors.FULL_GREEN, PredefinedNamedColors)
        self.assertIn(PredefinedNamedColors.FULL_BLUE, PredefinedNamedColors)

    def test_enum_member_attributes(self):
        red = PredefinedNamedColors.FULL_RED
        self.assertEqual("full red", red.colorname)
        self.assertEqual(255, red.red)
        self.assertEqual(0, red.green)
        self.assertEqual(0, red.blue)

    def test_enum_member_methods(self):
        red = PredefinedNamedColors.FULL_RED
        self.assertEqual("#ff0000", red.getHexString())
        green = PredefinedNamedColors.FULL_GREEN
        self.assertEqual("#00ff00", green.getHexString())
        blue = PredefinedNamedColors.FULL_BLUE
        self.assertEqual("#0000ff", blue.getHexString())


if __name__ == '__main__':
    unittest.main()
