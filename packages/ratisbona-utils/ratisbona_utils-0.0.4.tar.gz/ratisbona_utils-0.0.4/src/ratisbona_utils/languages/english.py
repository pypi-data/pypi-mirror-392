"""
    This module contains utility functions for the English language.
"""

def encode_english_short_ordinal(ith: int) -> str:
    """
        Encodes the given ordinal number as a short ordinal string.

        Examples:
            1 -> 1st
            2 -> 2nd
            ...
            10 -> 10th
            11 -> 11th
            ...
            20 -> 20th
            21 -> 21st
            ...
        Args:
            ith: The ordinal number to encode.

        Return:
            The encoded ordinal number.
         """
    if 4 <= ith % 100 <= 20 or 4 <= ith % 10 <= 9 or ith % 10 == 0:
        return f'{ith}th'
    return f'{ith}'+['st', 'nd', 'rd'][ith % 10 - 1]