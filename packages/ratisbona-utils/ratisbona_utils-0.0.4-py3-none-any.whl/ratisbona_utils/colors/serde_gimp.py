from io import StringIO
from pathlib import Path

from ratisbona_utils.colors.simple_color import RGBColor, NormalizedRGBColor
from ratisbona_utils.colors.palette import Palette


def to_gimp_palette(palette: Palette[RGBColor]) -> str:
    """
    Convert a Palette object to a GIMP palette file format.

    Args:
        palette (Palette): The palette object to convert

    Returns:
        str: The GIMP palette file content
    """
    description = palette.description.replace("\n", " ")
    lines = [
        "GIMP Palette",
        f"Name: {palette.name}",
        "Columns: 16",
        f"# Description: {description}",
        f"# Author: {palette.author}",
        f"# Created: {palette.creation_date}",
    ]
    for color, name in zip(palette.colors, palette.color_names):
        lines.append(f"{color[0]} {color[1]} {color[2]} {name}")
    return "\n".join(lines)


def parse_gimp_palette(palette_as_str: str) -> Palette:
    """
    Parse a GIMP palette file and return the Palette object.

    Args:
        palette_as_str (str): The GIMP palette file content as a string

    Returns:
        Palette: The parsed palette object
    """
    lines = palette_as_str.splitlines()
    lines = map(str.strip, lines)
    lines = list(filter(lambda s: s and not s.startswith("#"), lines))
    if not lines[0] == "GIMP Palette":
        raise ValueError("Not a GIMP palette file")
    lines = lines[1:]
    name = "?"
    while True:
        current_line = lines[0]

        if current_line.startswith("Name: "):
            name = current_line[6:]
            lines = lines[1:]
            continue

        if current_line.startswith("Columns: "):
            lines = lines[1:]
            continue

        break

    colors = []
    names = []
    for line in lines:
        if not line:
            continue
        color = line.split()
        colors.append((int(color[0]), int(color[1]), int(color[2])))
        names.append(color[3] if len(color) > 3 else "")
    return Palette(
        name=name,
        description="",
        author="",
        creation_date=None,
        colors=colors,
        color_names=names,
        color_types=["rgb"] * len(colors),
    )


def to_gimp_gradient(title: str, colors: list[NormalizedRGBColor]) -> str:
    """Generate a GIMP .ggr gradient file from a list of normalized RGB tuples."""
    num_segments = len(colors) - 1  # Number of segments

    if num_segments < 1:
        raise ValueError("At least two colors are needed to create a gradient.")

    f = StringIO()
    f.write("GIMP Gradient\n")
    f.write(f"Name: {title}\n")
    f.write(f"{num_segments}\n")  # Number of segments

    for i in range(num_segments):
        r1, g1, b1 = colors[i]
        r2, g2, b2 = colors[i + 1]
        start = i / num_segments
        end = (i + 1) / num_segments
        middle = (start + end) / 2  # Linear interpolation for midpoint

        # Format: start middle end  R1 G1 B1 A1  R2 G2 B2 A2  blend_type color_type
        f.write(
            f"{start:.6f} {middle:.6f} {end:.6f}   {r1:.6f} {g1:.6f} {b1:.6f} 1.0   {r2:.6f} {g2:.6f} {b2:.6f} 1.0   0 0\n")
    return f.getvalue()


