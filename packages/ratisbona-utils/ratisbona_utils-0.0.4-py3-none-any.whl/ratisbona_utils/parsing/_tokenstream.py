from dataclasses import dataclass, field
from typing import TypeVar, Generic, Generator, Iterable, Iterator

from ._model import LineToken

T = TypeVar('T')


@dataclass
class TokenStream(Generic[T]):
    """
    A stream of tokens that can be read and put back for backtracking.

    Args:
        tokenizer: A provider of tokens.
    """
    tokenizer: Iterator[T]
    buffer: list[T] = field(default_factory=list[T])

    def next_token(self):
        """
        Retrieves the next token from the stream.

        Returns:
            The next token, or None if the stream is exhausted.
        """
        if self.buffer:
            return self.buffer.pop()  # Retrieve the most recently put-back token
        return next(self.tokenizer)

    def put_back(self, token):
        """
        Puts a token back into the stream for backtracking.

        Args:
            token: The token to put back.
        """
        self.buffer.append(token)


def line_tokenizer(stream: Iterable[str]) -> Generator[LineToken, None, None]:
    """
    A generator function that yields LineTokens from a given stream.

    Args:
        stream: An iterable stream of lines (e.g., a file object or any iterable of strings).

    Yields:
        LineToken: A token representing a line of text with its line number.
    """
    for line_number, line in enumerate(stream, start=1):
        yield LineToken(text=line.rstrip('\n'), line_number=line_number)