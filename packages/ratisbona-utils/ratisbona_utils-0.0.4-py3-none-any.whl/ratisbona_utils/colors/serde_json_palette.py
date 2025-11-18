import json
from dataclasses import asdict
from datetime import datetime

from ratisbona_utils.colors import Palette, rgb_to_hex, hex_to_rgb
from ratisbona_utils.json import (
    simple_json_serializer,
    to_json_line,
    to_json_array_horizontal, to_json_object,
)


def to_json(palette: Palette) -> str:
    print(palette, type(palette))
    palette_dict = asdict(palette)
    ordinary_lines = [
        to_json_line(key, json.dumps(value))
        for key, value in palette_dict.items()
        if key not in ["colors", "color_names", "color_types", "creation_date"]
    ]
    creation_date_line = to_json_line(
        "creation_date",
        json.dumps(palette.creation_date.isoformat() if palette.creation_date else None),
    )
    color_names_line = to_json_line(
        "color_names",
        to_json_array_horizontal([json.dumps(name) for name in palette.color_names]),
    )
    color_types_line = to_json_line(
        "color_types",
        to_json_array_horizontal([json.dumps(type_) for type_ in palette.color_types]),
    )

    mangled_colors = []
    for color, colortype in zip(palette.colors, palette.color_types):
        if colortype == "rgb":
            mangled_colors.append(json.dumps(rgb_to_hex(color)))
        else:
            mangled_colors.append(json.dumps(color))
    colors_line = to_json_line("colors", to_json_array_horizontal(mangled_colors))
    return to_json_object(ordinary_lines + [creation_date_line, color_names_line, color_types_line, colors_line])


def from_json(json_text: str) -> Palette:
    """
    Deserialize a Palette object from a JSON string.
    Args:
        json_text: The JSON string to deserialize.

    Returns:
        Palette: The deserialized Palette object.
    """
    attributes = json.loads(json_text)

    if attributes["creation_date"]:
        attributes["creation_date"] = datetime.fromisoformat(attributes["creation_date"])

    remangled_colors = []
    for color, colortype in zip(attributes["colors"], attributes["color_types"]):
        if colortype == "rgb":
            remangled_colors.append(hex_to_rgb(color))
        else:
            remangled_colors.append(color)
    attributes["colors"] = remangled_colors
    return Palette(**attributes)

