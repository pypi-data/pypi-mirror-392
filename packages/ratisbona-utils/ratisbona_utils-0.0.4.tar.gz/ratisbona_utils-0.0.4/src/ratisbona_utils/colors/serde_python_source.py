from ratisbona_utils.colors import Palette, RGBColor


def to_sourcecode(palette: Palette[RGBColor]) -> str:

    text = ""
    for color, name in zip(palette.colors, palette.color_names):
        python_name = name.replace("-", "_")
        r, g, b = color
        text += f"{python_name}=({hex(r)}, {hex(g)}, {hex(b)})\n"

    capitalized_palette_name = palette.name.replace(" ", "_").upper()

    text += f"{capitalized_palette_name}=[\n"
    for name in palette.color_names:
        python_name = name.replace("-", "_")
        text += f"    {python_name},\n"
    text += "]"

    print(text)