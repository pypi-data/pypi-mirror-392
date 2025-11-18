import math
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, Generic

from ratisbona_utils.colors.simple_color import linear_blend, RGBColor, rgb_bounding

T = TypeVar("T")


@dataclass(frozen=True)
class Palette(Generic[T]):
    """
    A class to represent a palette of colors.

    Attributes:
        name (str): The name of the palette
        description (str): The description of the palette. Optional, use an empty string if not present
        author (str): The author of the palette. Optional, use an empty string if not present
        creation_date (datetime | None): The creation date of the palette. Optional, use None if not present
        colors (list[T]): The colors of the palette
        color_names (list[str]): The names of the colors. Must be the same length as colors.
        Allowed to contain empty strings.
        color_types (list[str]): The types of the colors. Must be the same length as colors
    """
    name: str
    description: str
    author: str
    colors: list[T]
    color_names: list[str]
    color_types: list[str]
    creation_date: datetime | None = None


def linear_interpolate_two_colors(
        color0: RGBColor,
        color1: RGBColor,
        num_colors: int,
        include_start=True
):
    maxcount = num_colors if include_start else num_colors + 1
    startcount = 0 if include_start else 1
    divider = maxcount - 1
    result = [
        linear_blend(color0, color1, i/divider, rgb_bounding)
        for i in range(startcount, maxcount)
    ]
    return result


def linear_interpolate(colors, num_destination_colors):
    num_source_colors = len(colors)
    num_colors_to_create = num_destination_colors
    num_colors_per_run = num_colors_to_create / (num_source_colors - 1)

    resulting_colors = []
    for i in range(num_source_colors - 1):
        num_colors_to_create_in_this_run = math.ceil(num_colors_per_run * (i + 1) - len(resulting_colors))
        resulting_colors.extend(
            linear_interpolate_two_colors(colors[i], colors[i + 1], num_colors_to_create_in_this_run, i == 0)
        )
    return resulting_colors