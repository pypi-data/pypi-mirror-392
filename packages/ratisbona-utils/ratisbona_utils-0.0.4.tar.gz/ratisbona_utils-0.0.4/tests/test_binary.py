import unittest

from ratisbona_utils.binary import BitStuffer, utf8_num_bytes, nth_char_offset
from ratisbona_utils.binary.binary_tools import BitUnstuffer


class TestBinary(unittest.TestCase):

    def test_bitstuffer_shoud_stuff_as_much_bits_as_requested(self):
        bit_stuffer = BitStuffer()
        bit_stuffer.stuff_bits(0xFE_CA_12_34, 32)
        bit_stuffer.flush()
        self.assertEqual(bit_stuffer.to_bytes(), b"\xfe\xca\x12\x34")

        bit_stuffer = BitStuffer()
        bit_stuffer.stuff_bits(0xFE_CA_12_34, 16)
        bit_stuffer.flush()
        self.assertEqual(
            bit_stuffer.to_bytes(),
            b"\x12\x34",
        )

        bit_stuffer = BitStuffer()
        bit_stuffer.stuff_bits(0xFE_CA_12_34, 8)
        bit_stuffer.flush()
        self.assertEqual(
            bit_stuffer.to_bytes(),
            b"\x34",
        )

    def test_bitstuffer_must_fill_up_to_next_byte_with_0_on_flush(self):
        bit_stuffer = BitStuffer()
        bit_stuffer.stuff_bits(0xFE_CA_12_34, 15)
        bit_stuffer.flush()
        self.assertEqual(bit_stuffer.to_bytes(), (0x12_34 << 1).to_bytes(2, "big"))

    def test_unstuffer_must_reconstruct_bits(self):
        bit_unstuffer = BitUnstuffer(b"\x12\x34\x56\x78\xab\xcd\xef")
        bits = bit_unstuffer.get_bits(8)
        self.assertEqual(0x12, bits)
        bits = bit_unstuffer.get_bits(8)
        self.assertEqual(bits, 0x34)
        bits = bit_unstuffer.get_bits(8)
        self.assertEqual(bits, 0x56)
        bits = bit_unstuffer.get_bits(8)
        self.assertEqual(bits, 0x78)
        bits = bit_unstuffer.get_bits(8)
        self.assertEqual(bits, 0xAB)
        bits = bit_unstuffer.get_bits(8)
        self.assertEqual(bits, 0xCD)
        bits = bit_unstuffer.get_bits(8)
        self.assertEqual(bits, 0xEF)

    def test_stuff_and_unstuff_bits(self):
        random_testdata_3x_2to33_bits = [
            [2, 2, 3],
            [7, 5, 5],
            [1, 14, 5],
            [2, 11, 25],
            [29, 28, 9],
            [46, 27, 105],
            [53, 253, 251],
            [382, 38, 390],
            [500, 381, 480],
            [930, 761, 81],
            [1660, 535, 1064],
            [908, 3558, 2767],
            [1407, 6494, 12771],
            [25518, 1411, 19081],
            [65443, 23188, 44789],
            [113048, 65580, 30403],
            [188816, 148995, 215689],
            [499048, 300758, 88917],
            [109909, 28447, 1038224],
            [1241379, 754010, 623709],
            [840621, 493003, 2146724],
            [7080578, 6633325, 5866086],
            [13514231, 15110624, 8439533],
            [24330854, 33165880, 6505710],
            [7295787, 55200039, 5178595],
            [28429607, 6099813, 26815720],
            [235411492, 44675367, 47901737],
            [383381405, 339357961, 304902964],
            [471193697, 515116583, 989066118],
            [1064575415, 1010707593, 509209638],
            [3943487889, 3111298040, 3128685376],
        ]
        stuffer = BitStuffer()
        for idx, testdata in enumerate(random_testdata_3x_2to33_bits):
            for value in testdata:
                stuffer.stuff_bits(value, idx+2)
        binary = stuffer.to_bytes()

        unstuffer = BitUnstuffer(binary)
        for idx, testdata in enumerate(random_testdata_3x_2to33_bits):
            print(f'Testing {idx+2} Bits...')
            for expect_value in testdata:
                is_value = unstuffer.get_bits(idx + 2)
                print(f'Expected: {expect_value:x} Got: {is_value:x}')
                self.assertEqual(is_value, expect_value)

    def test_utf8_num_bytes_must_report_correct_number_of_bytes(self):
        teststring = "ü😉afdßyäΩ€𝄞"
        for character in teststring:
            with self.subTest("Testing character", character=character):
                encoded = character.encode("utf-8")
                self.assertEqual(len(encoded), utf8_num_bytes(encoded[0]))

    def test_utf8_must_return_1_if_byte_starts_with_0b0(self):
        self.assertEqual(utf8_num_bytes(0b00000000), 1)
        self.assertEqual(utf8_num_bytes(0b01111111), 1)

    def test_utf8_num_bytes_must_raise_if_byte_starts_with_0b10(self):
        with self.assertRaises(ValueError):
            utf8_num_bytes(0b10000000)

    def test_utf8_num_bytes_must_return_correct_number_of_bytes(self):
        self.assertEqual(utf8_num_bytes(0b11000000), 2)
        self.assertEqual(utf8_num_bytes(0b11100000), 3)
        self.assertEqual(utf8_num_bytes(0b11110000), 4)

    def test_utf8_num_bytes_must_raise_if_byte_has_5_or_more_leading_1s(self):
        with self.assertRaises(ValueError):
            utf8_num_bytes(0b11111000)

    def test_nth_char_offset_must_return_correct_offset(self):
        teststring = "ü😉afdßyäΩ€𝄞"
        test_bytes = teststring.encode("utf-8")

        for idx, char in enumerate(teststring):
            with self.subTest("Testing char", char=char):
                offset = nth_char_offset(test_bytes, idx)
                length = utf8_num_bytes(test_bytes[offset])
                self.assertEqual(test_bytes[offset:offset+length], char.encode("utf-8"))

    def test_nth_char_offset_must_raise_if_char_requested_beyond_input(self):
        teststring = "ü😉afdßyäΩ€𝄞"
        test_bytes = teststring.encode("utf-8")

        with self.assertRaises(IndexError):
            nth_char_offset(test_bytes, 11)




if __name__ == "__main__":
    unittest.main()
