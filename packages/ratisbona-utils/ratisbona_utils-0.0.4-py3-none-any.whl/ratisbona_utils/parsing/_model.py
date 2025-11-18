from dataclasses import dataclass


@dataclass(frozen=True)
class LineToken:
    """
    A token representing a line of text.

    Args:
        text: The text of the line.
        line_number: The line number of the line in the text parsed. Can be used for error-messages
    """
    text: str
    line_number: int


@dataclass(frozen=True)
class ParseError:
    """
    A parse error that occurred during parsing.

    Args:
        message: The error message.
        line_number: The line number where the error occurred.
        near_pos: The position in the line where the error occurred.
    """
    message: str
    line_number: int
    near_pos: int | None