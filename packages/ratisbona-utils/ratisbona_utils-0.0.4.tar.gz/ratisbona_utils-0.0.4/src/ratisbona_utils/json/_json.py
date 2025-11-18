"""
Utilities for a very simplistic JSON serialization.
"""

import json
from typing import Sequence


def _obj_to_dict_or_string(obj: object) -> dict | str:
    """
    Convert an object to a dictionary or string.

    Args:
        obj (object): The object to convert

    Returns:
        dict: The dictionary representation of the object
    """
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


def simple_json_serializer(obj: object) -> str:
    """
    Serialize an object to a JSON string.

    Args:
        obj (object): The object to serialize

    Returns:
        str: The JSON string
    """
    return json.dumps(obj, default=_obj_to_dict_or_string, indent=2)


def to_json_object(json_lines: Sequence[str]) -> str:
    """
    Convert a list of JSON lines to a JSON object.

    Args:
        json_lines (Sequence[str]): The JSON lines to convert

    Returns:
        dict: The JSON object
    """
    json_text = "  " + ",\n  ".join(json_lines)
    return "{\n" + json_text + "\n}"


def to_json_array_horizontal(elements: Sequence[str]) -> str:
    """
    Convert a list of JSON elements to a JSON array.

    Args:
        elements (Sequence[str]): The JSON elements to convert

    Returns:
        str: The JSON array
    """
    json_text = ", ".join(elements)
    return "[" + json_text + "]"

def to_json_line(key: str, value: str) -> str:
    """
    Convert a key-value pair to a JSON line.

    Args:
        key (str): The key
        value (str): The value

    Returns:
        str: The JSON line
    """
    return f'"{key}": {value}'



def to_json_array_vertical(elements: Sequence[str]) -> str:
    """
    Convert a list of JSON elements to a JSON array.

    Args:
        elements:  The JSON elements to convert

    Returns: The JSON array

    """
    json_text = ",\n  ".join(elements)
    return "[\n  " + json_text + "\n]"