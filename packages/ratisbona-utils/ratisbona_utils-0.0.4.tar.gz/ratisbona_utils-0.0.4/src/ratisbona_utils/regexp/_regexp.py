
def lookahead(pattern: str) -> str:
    """
    This function takes a regex pattern and returns a modified pattern that uses lookahead assertions.

    Lookahead matches if the next characters match the given pattern, without consuming any these characters.

    For example `Isaac (?=Asimov)` matches `Isaac ` only if it is followed by `Asimov`, but does not consume `Asimov`.

    Args:
        pattern (str): The regex pattern to modify.

    Returns:
        str: The modified regex pattern with lookahead assertions.
    """

    # Add lookahead assertions at the beginning and end of the pattern
    return '(?=' + pattern + ')'

def negative_lookahead(pattern: str) -> str:
    """
    This function takes a regex pattern and returns a modified pattern that uses negative lookahead assertions.

    Negative lookahead matches if the next characters do not match the given pattern, without consuming any these characters.

    For example `Isaac (?!Asimov)` matches `Isaac ` only if it is NOT followed by `Asimov`, but does not consume `Asimov`.

    Args:
        pattern (str): The regex pattern to modify.

    Returns:
        str: The modified regex pattern with negative lookahead assertions.
    """

    # Add negative lookahead assertions at the beginning and end of the pattern
    return '(?!' + pattern + ')'

def lookbehind(pattern: str) -> str:
    """
    This function takes a regex pattern and returns a modified pattern that uses lookbehind assertions.

    Lookbehind matches if the previous characters match the given pattern, without consuming any these characters.

    For example `(?<=Isaac) Asimov` matches `Asimov` only if it is preceded by `Isaac`, but does not consume `Isaac`.

    The contained pattern must only match strings of a fixed length.
    For example `abc` and `a|b` are allowed, but things like `a*` or `a+` or `a{3,4}`are not.

    Args:
        pattern (str): The regex pattern to modify.

    Returns:
        str: The modified regex pattern with lookbehind assertions.
    """

    # Add lookbehind assertions at the beginning and end of the pattern
    return '(?<' + pattern + ')'

def negative_lookbehind(pattern: str) -> str:
    """
    This function takes a regex pattern and returns a modified pattern that uses negative lookbehind assertions.

    Negative lookbehind matches if the previous characters do not match the given pattern, without consuming any these characters.
    For example `(?!Isaac) Asimov` matches `Asimov` only if it is NOT preceded by `Isaac`, but does not consume `Isaac`.

    The contained pattern must only match strings of a fixed length.

    Args:
        pattern (str): The regex pattern to modify.

    Returns:
        str: The modified regex pattern with negative lookbehind assertions.
    """
    return '(?<!' + pattern + ')'

def with_word_boundaries(pattern: str) -> str:
    """
        Surrounds the given pattern with word boundaries.

        Args:
            pattern (str): The regex pattern to modify.

        Returns:
            str: The modified regex pattern with word boundaries.
    """
    return r'\b' + pattern + r'\b'

def named_matchgroup(name: str, pattern: str) -> str:
    """
        Creates a named match group for the given pattern.

        Args:
            name (str): The name of the match group.
            pattern (str): The regex pattern to modify.

        Returns:
            str: The modified regex pattern with a named match group.
    """
    return f'(?P<{name}>{pattern})'

def non_capturing_group(pattern: str) -> str:
    """
        Creates a non-capturing group for the given pattern.

        Args:
            pattern (str): The regex pattern to modify.

        Returns:
            str: The modified regex pattern with a non-capturing group.
    """
    return '(?:' + pattern + ')'

def any_of(*patterns: str) -> str:
    """
        Creates a regex pattern that matches any of the given patterns.

        Args:
            *patterns (str): The regex patterns to combine.

        Returns:
            str: The combined regex pattern.
    """
    return "[" + "".join(patterns) + "]"

def optional(pattern: str) -> str:
    """
        Creates a regex pattern that matches the given pattern zero or one time.

        Args:
            pattern (str): The regex pattern to modify.

        Returns:
            str: The modified regex pattern with optional matching.
    """
    return f"({pattern})?"