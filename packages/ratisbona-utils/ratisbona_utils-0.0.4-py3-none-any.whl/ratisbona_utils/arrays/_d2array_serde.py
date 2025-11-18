import re
from typing import Callable

from ._d2array import D2Array

CellSerializer = Callable[[object], str]
CellParser = Callable[[str], object]

def d2array_to_separated(
        d2array: D2Array,
        separator: str = ',',
        line_separator: str = '\n',
        cell_serializer: CellSerializer = str
) -> str:
    """
    Serialize a D2Array into a string with separated values.

    Args:
        d2array: The D2Array to serialize.
        separator:  A string used to separate individual cell values. Default: ','
        line_separator: A string used to separate lines (rows). Default: '\n'
        cell_serializer: A function to serialize individual cell values to strings. Default: str.

    Returns:
        A string representation of the D2Array with separated values.
    """
    result = ""
    cols = d2array.num_cols
    for idx, cell in enumerate(d2array):
        result += cell_serializer(cell)
        if (idx + 1) % cols == 0:
            result += line_separator
        else:
            result += separator
    return result


def separated_to_d2array(
        data: str,
        separator_char: str = ',',
        escaping_char: str = '\\',
        line_separator: str = '\n',
        cell_parser: CellParser = lambda x: x
) -> D2Array:
    """
    Deserialize a string with separated values into a D2Array.

    Args:
        data: The input string containing the separated values.
        separator_char: A char used to separate individual cell values. Default: ','
        escaping_char: A char used to escape separator and line separator characters. Default: '\\'
        line_separator: A char used to separate lines (rows). Default: '\n'
        cell_parser: A function to parse individual cell values from strings. Default: identity function.

    Returns:
        A D2Array constructed from the parsed data.

    """
    line_split_re = f'(?<!{escaping_char}){line_separator}'
    sep_split_re = f'(?<!{escaping_char}){separator_char}'

    lines = [line for line in re.split(line_split_re, data) if line]
    rows = []
    for line in lines:
        cells = [cell for cell in re.split(sep_split_re, line) if cell]
        parsed_cells = [cell_parser(cell) for cell in cells]
        rows.append(parsed_cells)

    return D2Array.from_2d_list(rows)

