from typing import TypeVar

from ratisbona_utils.markdown import Heading
from ratisbona_utils.monads.monads import ResultMonad
from ratisbona_utils.parsing import TokenStream, LineToken, ParseError

T = TypeVar("T")


def _err(
    message: str, line_number: int, near_pos: int | None
) -> ResultMonad[T, ParseError]:
    return ResultMonad[T, ParseError].err(
        ParseError(
            message=message,
            line_number=line_number,
            near_pos=near_pos,
        )
    )


def try_parse_heading(
    line_token_stream: TokenStream[LineToken],
) -> ResultMonad[Heading, ParseError]:
    """
    Tries to parse a heading from the given token stream.

    Args:
        line_token_stream: The token stream to parse from.

    Returns:
        ResultMonad[Heading, ParseError]: A result monad containing the parsed heading or a parse error.
    """
    line_token = line_token_stream.next_token()
    if not line_token.text.startswith("#"):
        line_token_stream.put_back(line_token)
        return _err(
            f"Expected a heading to begin with # but got {line_token[:10]}",
            line_token.line_number, 0
        )

    level = 1
    while line_token.text[level] == "#":
        level += 1

    text = line_token.text[level:].strip()
    return ResultMonad.ok(Heading(level=level, text=text))

def try_parse_paragraph(
    line_token_stream: TokenStream[LineToken],
) -> ResultMonad[Paragraph, ParseError]:
    """
    Tries to parse a paragraph from the given token stream.

    Args:
        line_token_stream: The token stream to parse from.

    Returns:
        ResultMonad[Paragraph, ParseError]: A result monad containing the parsed paragraph or a parse error.
    """
    line_token = line_token_stream.next_token()
    if line_token.text.startswith("#"):
        line_token_stream.put_back(line_token)
        return _err(
            f"Expected a paragraph but got a heading",
            line_token.line_number, 0
        )

    content = []
    while line_token.text:
        content.append(PureText(line_token.text))
        line_token = line_token_stream.next_token()

    return ResultMonad.ok(Paragraph(content=content))