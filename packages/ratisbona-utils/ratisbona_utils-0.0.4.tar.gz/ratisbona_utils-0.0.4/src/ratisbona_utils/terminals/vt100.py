from enum import Enum
from typing import Iterable, Optional

from ratisbona_utils.colors import RGBComponent, RGBColor


class TerminalColor(int, Enum):
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7
    NONE = 999

    def escape(self, bright=True, background=False) -> str:
        if self == TerminalColor.NONE:
            return "\033[0m"
        return (
            f"\033[{'1' if bright else '0'};{'4' if background else '3'}{self.value}m"
        )


def rgb_terminal_escape(rgb: RGBColor, background=False) -> str:
    r, g, b = rgb
    return f"\033[{'48' if background else '38'};2;{r};{g};{b}m"


def color_block(rgb: RGBColor) -> str:
    """
    Prints a block of text with the specified RGB color as background.

    Args:
       rgb (RgbColor): The RGB color to use.
    """
    return rgb_terminal_escape(rgb, background=True) + " " + TerminalColor.NONE.escape()


def color_text(
    text: str, *, foreground: Optional[RGBColor], background: Optional[RGBColor] = None
) -> str | list[str]:
    """
    Prints text in the specified RGB color.

    Args:
        text (str): The text to print.
        foreground (RGBColor): The RGB color to use for the text. Set to none for "leave unchanged".
        background (RGBColor): The RGB color to use for the background. Set to none for "leave unchanged".
    """

    sequence = ""
    if foreground:
        sequence += rgb_terminal_escape(foreground)
    if background:
        sequence += rgb_terminal_escape(background, background=True)

    last_char_is_newline = text[-1] == "\n"

    results = ""
    for line in text.splitlines():
        if len(results) > 0:
            results += "\n"
        results += sequence + line + TerminalColor.NONE.escape()
    if last_char_is_newline:
        results += "\n"

    return results
