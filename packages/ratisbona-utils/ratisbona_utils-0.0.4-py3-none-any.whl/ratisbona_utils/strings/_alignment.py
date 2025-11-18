import re
from enum import Enum, auto
from itertools import zip_longest
import textwrap


class Alignment(Enum):
    """
    Base class for enums.
    """

    LEFT = auto()
    RIGHT = auto()
    CENTER = auto()
    BLOCK = auto()


ALIGNMENT_FUNCTIONS = {
    Alignment.LEFT: str.ljust,
    Alignment.RIGHT: str.rjust,
    Alignment.CENTER: str.center,
    Alignment.BLOCK: lambda text, width: text,
}


def align(text: str, width=80, alignment=Alignment.LEFT) -> str:
    """
    Align text in a given width.

    Args:
        text: The text to align.
        width: The width to align the text in.
        alignment: The alignment to use.

    Returns:
        str, the aligned text.
    """
    return ALIGNMENT_FUNCTIONS[alignment](text, width)


def longest_line(multiline_text: str) -> int:
    return max(len(line) for line in multiline_text.splitlines())


def zip_longest_textcolumn(*args: str, separator: str = " ") -> str:
    """
    Given several multiline texts (as lists of lines), this function will zip them together as columns, which each
    text you gave forming one column. The columns will be aligned to the left.

    Args:
        *args: The multiline texts.

        separator: The separator to use between the columns.

    Returns:
        The multiline text arranged as multiple columns.
    """

    colwidths = [longest_line(arg) for arg in args]

    split_args = [arg.splitlines() for arg in args]
    result = ""
    for idx, lines in enumerate(zip_longest(*split_args, fillvalue="")):
        result += (
            separator.join(line.ljust(width) for line, width in zip(lines, colwidths))
            + "\n"
        )
    return result


def shorten(
    text: str,
    max_length: int
) -> str:
    """
    Shorten a text to a maximum length, using an elipsis provider to provide the elipsis text.

    Args:
        text: The text to shorten.
        max_length: The maximum length of the text.
        elipsis_provider: A function that takes the length of the text and returns the elipsis text.
        elipsis_length: The length of the elipsis text.
    """
    TOO_LONG_REPLACEMENT="...[>999]..."
    LEAST_LENGTH = len(TOO_LONG_REPLACEMENT) + 2

    if max_length < LEAST_LENGTH:
        raise ValueError(f"max_length must be at least {LEAST_LENGTH}")

    length = len(text)
    if length <= max_length:
        return text

    elipsis = f"...[{length}]..." if length < 1000 else TOO_LONG_REPLACEMENT
    elipsis_length = len(elipsis)

    length_before_elipsis = (max_length - elipsis_length) // 2
    length_after_elipsis = max_length - elipsis_length - length_before_elipsis
    return text[:length_before_elipsis] + elipsis + text[-length_after_elipsis:]


def indent(text: str, indent: int) -> str:
    """
    Indent a text by a given number of spaces.

    Args:
        text: The text to indent.
        indent: The number of spaces to indent the text by.

    Returns:
        The indented text.
    """
    return "".join([
        f"{' ' * indent}{line}"
        for line in text.splitlines(keepends=True)
    ])

def rewrap_text(text: str, width: int) -> str:
    """Rewraps a string to a given column width, preserving existing double newlines.

    Args:
        text (str): The input text to rewrap.
        width (int): The maximum column width.

    Returns:
        str: The rewrapped text.
    """
    longest_line = max(len(line) for line in text.splitlines())
    if longest_line <= width:
        return text
    # Replace all single newlines in text by space. Keep double newlines.
    text = re.sub(r'(?<!\n)\n(?!(\n|\s))', ' ', text)
    return wrap_text(text, width)


def wrap_text(text, width):
    """Wraps a string to a given column width, preserving existing newlines.

    Args:
        text (str): The input text to wrap.
        width (int): The maximum column width.

    Returns:
        str: The wrapped text.
    """
    wrapped_lines = []

    for line in text.splitlines():  # Preserve existing newlines
        wrapped_lines.extend(
            textwrap.fill(line.strip(), width, break_long_words=True, break_on_hyphens=True).split("\n")
        )

    return "\n".join(wrapped_lines)

def si_format_number(the_number: int, binary_units=True) -> str:
    """
    Formats a number in SI units.

    Args:
        the_number (int): The number to format.
        binary_units (bool): Whether to use binary units (1024) or decimal units (1000).

    Returns:
        str: The formatted number, like '12M' or '12Mi'.
    """
    base = 1024 if binary_units else 1000
    postfix = ['',' k',' M',' G',' T']
    times = 0
    while the_number >= base and times < len(postfix):
        the_number = the_number // base
        times += 1
    return f'{the_number}{postfix[times]}' + ('i' if binary_units and times > 0 else '')
