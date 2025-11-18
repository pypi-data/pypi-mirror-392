import re
from dataclasses import dataclass
from typing import List, Optional, Generic, TypeVar, Callable, Tuple
import bisect

DEBUG = False

dprint = print if DEBUG else lambda *args, **kwargs: None



# Type alias for clarity.
RegularExpression = str
Position = int
LineNum = int
ColNum = int

@dataclass(frozen=True)
class TokenDefinition:
    token_type_name: str
    token_type_regexp: RegularExpression


T = TypeVar("T")


@dataclass(frozen=True)
class Token(Generic[T]):
    token_type_name: str
    token_full_match: str
    token_match_groups: dict[str, str]
    token_match_start_pos: int
    token_match_end_pos: int


def get_tokenizer(token_definitions: List[TokenDefinition]):

    # Precompile the regexes for efficiency.
    compiled_defs = []
    for tokendef in token_definitions:
        dprint("Compiling token definition:", tokendef.token_type_name, tokendef.token_type_regexp)
        compiled_defs.append(
            re.compile(tokendef.token_type_regexp)
        )


    def tokenize(text: str) -> List[Token]:

        pos = 0
        while pos < len(text):
            # Track the best match found among all token definitions.
            earliest_match: Optional[re.Match] = None
            best_token_def: Optional[TokenDefinition] = None

            # Check every token definition for a match somewhere in the remaining text.
            for token_def, pattern in zip(token_definitions, compiled_defs):
                match = pattern.search(text, pos)
                if match is None:
                    continue

                # If this is the first match, or if it occurs earlier than the best so far,
                # update the best match.
                if earliest_match is None or match.start() < earliest_match.start():
                    earliest_match = match
                    best_token_def = token_def
                # If two matches start at the same position, pick the one with the longer match.
                elif match.start() == earliest_match.start():
                    if (
                        match.end() - match.start()
                        > earliest_match.end() - earliest_match.start()
                    ):
                        earliest_match = match
                        best_token_def = token_def

            if earliest_match is None:
                # No token definition matched the remainder of the text.
                the_text = text[pos:].strip()
                if the_text: # Only yield a "Text" token if there is non-empty unmatched text.
                    yield Token(
                        token_type_name="Text",
                        token_full_match=the_text,
                        token_match_groups={},
                        token_match_start_pos=pos,
                        token_match_end_pos=len(text),
                    )
                    break

            # If there is unmatched text before the earliest match, add it as a "Text" token.
            if earliest_match.start() > pos:
                the_text = text[pos: earliest_match.start()].strip()
                if the_text:
                    yield Token(
                        token_type_name="Text",
                        token_full_match=the_text,
                        token_match_groups={},
                        token_match_start_pos=pos,
                        token_match_end_pos=earliest_match.start(),
                    )

            # Add the matched token.
            yield Token(
                token_type_name=best_token_def.token_type_name,
                token_full_match=earliest_match.group(0),
                token_match_groups=earliest_match.groupdict(),
                token_match_start_pos=earliest_match.start(),
                token_match_end_pos=earliest_match.end(),
            )
            pos = earliest_match.end()

            # To avoid getting stuck if a pattern matches a zero-length string.
            if pos == earliest_match.start():
                pos += 1

    return tokenize


def create_position_mapper(text: str) -> Callable[[Position], Tuple[LineNum, ColNum]]:
    """
    Create a mapping function from a character index to a (line, column) tuple.
    The mapping function returns 1-indexed line and column numbers.

    Parameters:
      text (str): The text to map positions from.

    Returns:
      Callable[[int], Tuple[int, int]]: A function that maps a character index to (line, column).
    """
    # Precompute newline positions.
    # Adding -1 at the beginning so that the first line starts at position 0.
    newline_positions = [-1] + [i for i, char in enumerate(text) if char == "\n"]

    def map_position(pos: int) -> Tuple[int, int]:
        """
        Map a given character index to a (line, column) tuple.

        Parameters:
          pos (int): The zero-based character index in text.

        Returns:
          Tuple[int, int]: A tuple (line, column) with both numbers starting at 1.
        """
        # Find the line number using bisect.
        # bisect_right finds an insertion point so that newline_positions remains sorted.
        line_index = bisect.bisect_right(newline_positions, pos) - 1
        # The start of the current line is one character after the previous newline.
        line_start = newline_positions[line_index] + 1
        column = pos - line_start
        # Return 1-indexed line and column numbers.
        return line_index + 1, column + 1

    return map_position


# Example usage:
if __name__ == "__main__":
    sample_text = "Hello world!\nThis is a test.\nAnother line."
    pos_mapper = create_position_mapper(sample_text)

    # Let's map a few positions:
    positions = [0, 5, 12, 13, 25, len(sample_text) - 1]
    for pos in positions:
        line, col = pos_mapper(pos)
        print(
            f"Position {pos}: line {line}, column {col}: >{sample_text[max(pos-1,0):pos+2]}<"
        )
