def utf8_num_bytes(the_first_byte: int) -> int:
    """
    Returns the number of bytes in a UTF-8 character, given the first byte.

    Args:
        the_first_byte (int): The first byte of the UTF-8 character.

    Returns:
        int: The number of bytes in the UTF-8 character
    """
    for count in range(0, 5):
        if not (the_first_byte & 0x80):
            # Number of leading 1's is number of bytes, except its starts with 0, then it's one byte.
            if count == 0:
                return 1
            # Starting out with 10 is invalid!
            if count == 1:
                raise ValueError("Invalid as UTF-8 first character. Cannot start with 0b10...")
            return count

        the_first_byte = (the_first_byte << 1) & 0xFF
    raise ValueError("Invalid as UTF-8 first character. Seems to indicate more than 4 bytes?!??")


def nth_char_offset(the_bytes: bytes | bytearray, n: int, offset=0):
    """
    Returns the offset of the nth UTF-8 character in a byte array.

    Args:
        the_bytes (bytes | bytearray): The byte array.
        n (int): The index of the character.
        offset (int): The offset to start searching from.
    """
    for count in range(0, n + 1):
        if count >= n:
            return offset
        offset += utf8_num_bytes(the_bytes[offset])
        if offset >= len(the_bytes):
            raise IndexError(f"Index out of range. Cannot find {n} characters in byte array.")
    raise AssertionError("Code should never reach this point!")