import inspect
import re
from typing import Callable, Sequence
from unidecode import unidecode
from transliterate import translit
from transliterate.exceptions import LanguageDetectionError

CommandOption = str

cleaners: dict[CommandOption, tuple[Callable[[str], str], str]] = {}

# According to ttps://help.interfaceware.com/v6/windows-reserved-file-names
FORBIDDEN_IN_WINDOWS = r'< > : " / \ | ? *'.split(" ")
FORBIDDEN_IN_WINDOWS_REPLACE_BY = [
    "_lt_",
    "_gt_",
    "_colon_",
    "_quote_",
    "_slash_",
    "_bslash_",
    "_bar_",
    "_qm_",
    "_star_",
]
UMLAUTS = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"}
MULTIPLE_UNDERSCORES_PATTERN = re.compile(r"_{2,}")
MULTIPLE_POINTS_PATTERN = re.compile(r"\.{2,}")
MULTIPLE_DASHES_PATTERN = re.compile(r"-{2,}")
MULITPLE_UNDERSCORE_DASH_PATTERN = re.compile(r"(_-)+_?")
MULITPLE_SPACE_PATTERN = re.compile(r" +")
JUNK_BEFORE_SUFFIX_PATTERN = re.compile(r"[-_ ]+(\.[^\.]+)$")


def get_docstring_summary(func):
    """Returns the first paragraph of a function's docstring (up to the first empty line)."""
    doc = inspect.getdoc(func)  # Get the cleaned-up docstring (None if no docstring)
    if not doc:
        return None  # Return None if there's no docstring

    # Split by lines and stop at the first empty line
    lines = doc.split("\n")
    summary_lines = []

    for line in lines:
        if line.strip() == "":
            break  # Stop at the first empty line
        summary_lines.append(line)

    return " ".join(summary_lines)  # Join lines into a single string


def _register_cleaner(function: Callable[[str], str]):
    name = function.__name__.replace("sclean_", "")
    docsummary = get_docstring_summary(function)

    cleaners[name] = (function, docsummary)


def sclean_transliterate(current_string: str) -> str:
    """
    Transliterate the string to a latin alphabet representation. This is useful for example for filenames that should
    not contain special characters.

    Args:
        current_string (str): The string to transliterate

    Returns:
        str: The transliterated string
    """
    try:
        return translit(current_string, reversed=True)
    except LanguageDetectionError:
        return current_string


_register_cleaner(sclean_transliterate)


def sclean_unidecode(current_string: str) -> str:
    """
    Unidecode the string to a latin alphabet representation. This is useful for example for filenames that should
    not contain special characters.

    Args:
        current_string (str): The string to unidecode

    Returns:
        str: The unidecoded string

    """
    return unidecode(current_string)


_register_cleaner(sclean_unidecode)


def sclean_tolower(current_string: str) -> str:
    """
    Convert the string to lowercase.

    Args:
        current_string (str): The string to convert

    Returns:
        str: The lowercase string
    """
    return current_string.lower()


_register_cleaner(sclean_tolower)


def sclean_samba_conform(current_string: str) -> str:
    """
    Replace all glyphs that windows won't like in filenames, like < > : " / \\ | ? *

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    for forbidden, replacement in zip(
            FORBIDDEN_IN_WINDOWS, FORBIDDEN_IN_WINDOWS_REPLACE_BY
    ):
        current_string = current_string.replace(forbidden, replacement)
    return current_string


_register_cleaner(sclean_samba_conform)


def sclean_umlauts(current_string: str) -> str:
    """
    Replace all umlauts with their latin alphabet representation, like äöüÄÖÜß -> ae oe ue Ae Oe Ue ss

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    for umlaut, replacement in UMLAUTS.items():
        current_string = current_string.replace(umlaut, replacement)
    return current_string


_register_cleaner(sclean_umlauts)


def sclean_despace(current_string: str) -> str:
    """
    Replace all spaces with underscores

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.replace(" ", "_")


_register_cleaner(sclean_despace)


def sclean_escape(current_string: str) -> str:
    """
    Replace all escape sequences with '_esc_'

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.replace("\x1b", "_esc_")


_register_cleaner(sclean_escape)


def sclean_parentesis(current_string: str) -> str:
    """
    Remove all parentesis

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.replace("(", "").replace(")", "")


_register_cleaner(sclean_parentesis)


def sclean_brackets(current_string: str) -> str:
    """
    Remove all brackets

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.replace("[", "").replace("]", "")


_register_cleaner(sclean_brackets)


def sclean_curly_brackets(current_string: str) -> str:
    """
    Remove all curly brackets

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.replace("{", "").replace("}", "")


_register_cleaner(sclean_curly_brackets)


def sclean_leading_space(current_string: str) -> str:
    """
    Remove leading spaces

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.lstrip()


_register_cleaner(sclean_leading_space)


def sclean_trailing_space(current_string: str) -> str:
    """
    Remove trailing spaces

    Args:
        current_string (str): The string to convert
    Returns:
        str: The cleaned string
    """
    return current_string.rstrip()


_register_cleaner(sclean_trailing_space)


def sclean_leading_dash(current_string: str) -> str:
    """
    Remove leading dashes

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.lstrip("-")


_register_cleaner(sclean_leading_dash)


def sclean_trailing_dash(current_string: str) -> str:
    """
    Remove trailing dashes

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.rstrip("-")


_register_cleaner(sclean_trailing_dash)


def sclean_leading_underscore(current_string: str) -> str:
    """
    Remove leading underscores

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.lstrip("_")


_register_cleaner(sclean_leading_underscore)


def sclean_trailing_underscore(current_string: str) -> str:
    """
    Remove trailing underscores

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.rstrip("_")


_register_cleaner(sclean_trailing_underscore)



def sclean_commas(current_string: str) -> str:
    """
    Remove all commas

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.replace(",", "")


_register_cleaner(sclean_commas)


def sclean_exclamation_marks(current_string: str) -> str:
    """
    Remove all exclamation marks

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.replace("!", "")


_register_cleaner(sclean_exclamation_marks)


def sclean_single_quotes(current_string: str) -> str:
    """
    Remove all single quotes

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.replace("'", "")


_register_cleaner(sclean_single_quotes)


def sclean_multiple_points(current_string: str) -> str:
    """
    Replace multiple points with a single point

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return MULTIPLE_POINTS_PATTERN.sub(".", current_string)


_register_cleaner(sclean_multiple_points)


def sclean_ampers_and(current_string: str) -> str:
    """
    Replace ampersands with 'and'

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.replace("&", "and")


_register_cleaner(sclean_ampers_and)


def sclean_backticks(current_string: str) -> str:
    """
    Remove all backticks

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.replace("`", "")


_register_cleaner(sclean_backticks)


def scclean_dollar_sign(current_string: str) -> str:
    """
    Remove all dollar signs

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return current_string.replace("$", "_dollar_")


_register_cleaner(scclean_dollar_sign)


def sclean_multiple_dashes(current_string: str) -> str:
    """
    Replace multiple dashes with a single dash

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return MULTIPLE_DASHES_PATTERN.sub("-", current_string)


_register_cleaner(sclean_multiple_dashes)

def sclean_multiple_underscores(current_string: str) -> str:
    """
    Replace multiple underscores with a single underscore

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return MULTIPLE_UNDERSCORES_PATTERN.sub("_", current_string)


_register_cleaner(sclean_multiple_underscores)


def sclean_dashes_before_suffix(current_string: str) -> str:
    """
    Remove dashes, whitespace or underscores before a suffix

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    while match := JUNK_BEFORE_SUFFIX_PATTERN.search(current_string):
        current_string = current_string.replace(match.group(0), match.group(1))
    return current_string


_register_cleaner(sclean_dashes_before_suffix)


def sclean_multiple_spaces(current_string: str) -> str:
    """
    Replace multiple spaces with a single space

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return MULITPLE_SPACE_PATTERN.sub(" ", current_string)


_register_cleaner(sclean_multiple_spaces)

def sclean_multiple_underscores_dashes(current_string: str) -> str:
    """
    Replace multiple underscores with a single _-_

    Args:
        current_string (str): The string to convert

    Returns:
        str: The cleaned string
    """
    return MULITPLE_UNDERSCORE_DASH_PATTERN.sub("_-_", current_string)


_register_cleaner(sclean_multiple_underscores_dashes)


def string_cleaner(
        current_string: str,
        apply_cleaners: Sequence[str],
        change_callback: Callable[[str, str, str], None] = None,
) -> str:
    """
    Clean a string according to a list of cleaners.

    Args:
        current_string (str): The string to clean
        apply_cleaners (Sequence[str]): The cleaners to apply
        change_callback (Callable[[str, str, str], None], optional): A callback to call when a cleaner changes the string. Defaults to None.
    """
    for cleaner in apply_cleaners:
        if not cleaner in cleaners:
            raise ValueError(f"Unknown cleaner {cleaner}")

    for cleaner in apply_cleaners:
        new_string = cleaners[cleaner][0](current_string)
        if change_callback and new_string != current_string:
            change_callback(cleaner, current_string, new_string)
        current_string = new_string
    return current_string


def main():
    print("Available cleaners:")
    for cleaner, doc in cleaners.items():
        print(f"{cleaner:35s}: {doc[1]}")

if __name__ == "__main__":
    main()