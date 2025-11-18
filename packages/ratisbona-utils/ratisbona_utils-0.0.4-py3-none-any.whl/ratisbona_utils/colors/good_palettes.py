from ratisbona_utils.colors import normalized_to_rgb, Palette
from ratisbona_utils.colors.palette_generators import (
    ega_num_to_rgb,
    cga_num_to_normalized_rgb,
)
from ratisbona_utils.colors.simple_color import hex_to_rgb, lab_lighten_rgb

ULIS_WEBCOLORS_HEX = [
    "#993300",
    "#CC0000",
    "#FF6600",
    "#FFCC00",
    "#99CC00",
    "#009900",
    "#00CCCC",
    "#0099FF",
    "#0000CC",
    "#6600CC",
    "#CC00CC",
]

ULIS_WEBCOLORS_RGB = [hex_to_rgb(hexcolor) for hexcolor in ULIS_WEBCOLORS_HEX]
ULIS_WEBCOLORS_PALETTE = Palette(
    name="Ulis Webcolors",
    description="The webcolors of Ulrich",
    author="Ulrich",
    colors=ULIS_WEBCOLORS_RGB,
    color_names=[
        "brown",
        "red",
        "orange",
        "yellow",
        "lime",
        "green",
        "cyan",
        "lightblue",
        "blue",
        "violet",
        "magenta",
    ],
    color_types=["rgb"] * len(ULIS_WEBCOLORS_RGB),
)

FIRE_PALETTE_HEX = [
    "#0000cc",
    "#3333ff",
    "#33ffff",
    #'#330033',
    "#ffff00",
    "#ffff33",
    "#ffcc00",
    "#ff0000",
    "#cc0000",
    "#660000",
    "#000000",
]

FIRE_PALETTE_RGB = [hex_to_rgb(hexcolor) for hexcolor in reversed(FIRE_PALETTE_HEX)]
FIRE_PALETTE = Palette(
    name="Fire",
    description="A fire palette",
    author="Ulrich",
    colors=FIRE_PALETTE_RGB,
    color_names=[
        "blue",
        "lightblue",
        "cyan",
        #'purple',
        "yellow",
        "brightyellow",
        "orange",
        "red",
        "darkred",
        "darkdarkred",
        "black",
    ],
    color_types=["rgb"] * len(FIRE_PALETTE_RGB),
)

EGA_PALETTE_RGB = [ega_num_to_rgb(i) for i in range(64)]
EGA_PALETTE = Palette(
    name="EGA",
    description="The EGA palette",
    author="IBM",
    colors=EGA_PALETTE_RGB,
    color_names=[
        "black",
        "blue",
        "green",
        "cyan",
        "red",
        "magenta",
        "brown",
        "lightgray",
        "darkgray",
        "lightblue",
        "lightgreen",
        "lightcyan",
        "lightred",
        "lightmagenta",
        "yellow",
        "white",
    ],
    color_types=["rgb"] * len(EGA_PALETTE_RGB),
)

CGA_PALETTE_RGB = [normalized_to_rgb(cga_num_to_normalized_rgb(i)) for i in range(16)]
CGA_PALETTE = Palette(
    name="CGA",
    description="The CGA palette",
    author="IBM",
    colors=CGA_PALETTE_RGB,
    color_names=[
        "black",
        "darkblue",
        "darkgreen",
        "darkcyan",
        "darkred",
        "darkmagenta",
        "brown",
        "lightgray",
        "darkgray",
        "lightblue",
        "lightgreen",
        "lightcyan",
        "lightred",
        "lightmagenta",
        "yellow",
        "white",
    ],
    color_types=["rgb"] * len(CGA_PALETTE_RGB),
)

AMIGA_PALETTE_RGB = [(0, 85, 170), (255, 255, 255), (0, 0, 0), (255, 136, 0)]
AMIGA_PALETTE = Palette(
    name="Amiga",
    description="The Amiga palette of Workbench 1.x",
    author="Commodore",
    colors=AMIGA_PALETTE_RGB,
    color_names=["blue", "white", "black", "orange"],
    color_types=["rgb"] * len(AMIGA_PALETTE_RGB),
)

solarized_base03 = (0x0, 0x2B, 0x36)
solarized_base02 = (0x7, 0x36, 0x42)
solarized_base01 = (0x58, 0x6E, 0x75)
solarized_base00 = (0x65, 0x7B, 0x83)
solarized_base0 = (0x83, 0x94, 0x96)
solarized_base1 = (0x93, 0xA1, 0xA1)
solarized_base2 = (0xEE, 0xE8, 0xD5)
solarized_base3 = (0xFD, 0xF6, 0xE3)
solarized_yellow = (0xB5, 0x89, 0x0)
solarized_orange = (0xCB, 0x4B, 0x16)
solarized_red = (0xDC, 0x32, 0x2F)
solarized_magenta = (0xD3, 0x36, 0x82)
solarized_violet = (0x6C, 0x71, 0xC4)
solarized_blue = (0x26, 0x8B, 0xD2)
solarized_cyan = (0x2A, 0xA1, 0x98)
solarized_green = (0x85, 0x99, 0x0)

SOLARIZED_COLORS_BASE = [
    solarized_base03,
    solarized_base02,
    solarized_base01,
    solarized_base00,
    solarized_base0,
    solarized_base1,
    solarized_base2,
    solarized_base3,
]

SOLARIZED_COLORS_COLORS = [
    solarized_red,
    solarized_orange,
    solarized_yellow,
    solarized_green,
    solarized_cyan,
    solarized_blue,
    solarized_violet,
    solarized_magenta,
]

SOLARIZED_COLORS = SOLARIZED_COLORS_BASE + SOLARIZED_COLORS_COLORS
SOLARIZED_COLORS_PALETTE = Palette(
    name="Solarized",
    description="The Solarized palette",
    author="Ethan Schoonover",
    colors=SOLARIZED_COLORS,
    color_names=[
        "base03",
        "base02",
        "base01",
        "base00",
        "base0",
        "base1",
        "base2",
        "base3",
        "red",
        "orange",
        "yellow",
        "green",
        "cyan",
        "blue",
        "violet",
        "magenta",
    ],
    color_types=["rgb"] * len(SOLARIZED_COLORS),
)

SOLARIZED_COLORS_EXTENDED = (
    SOLARIZED_COLORS
    + [lab_lighten_rgb(color, 20) for color in SOLARIZED_COLORS_COLORS]
    + [lab_lighten_rgb(color, -20) for color in SOLARIZED_COLORS_COLORS]
)
SOLARIZED_COLORS_EXTENDED_PALETTE = Palette(
    name="Solarized Extended",
    description="The Solarized palette with lightened and darkened colors",
    author="Ulrich Schwenk, based on work by Ethan Schoonover",
    colors=SOLARIZED_COLORS_EXTENDED,
    color_names=[
        "base03",
        "base02",
        "base01",
        "base00",
        "base0",
        "base1",
        "base2",
        "base3",
        "red",
        "orange",
        "yellow",
        "green",
        "cyan",
        "blue",
        "violet",
        "magenta",
        "red_light",
        "orange_light",
        "yellow_light",
        "green_light",
        "cyan_light",
        "blue_light",
        "violet_light",
        "magenta_light",
        "red_dark",
        "orange_dark",
        "yellow_dark",
        "green_dark",
        "cyan_dark",
        "blue_dark",
        "violet_dark",
        "magenta_dark",
    ],
    color_types=["rgb"] * len(SOLARIZED_COLORS_EXTENDED),
)

SOLARIZED_COLORS_ANSI_TERMINAL_NAMES = [
    "Background", "Black",         "Red",          "Green",        "Yellow",         "Blue",         "Magenta",         "Cyan",         "White",
    "Foreground", "Bright Black",  "Bright Red",   "Bright Green", "Bright Yellow",  "Bright Blue",  "Bright Magenta",  "Bright Cyan",  "Bright White"
]

SOLARIZED_COLORS_ANSI_TERMINAL_HEX = [
    "#163540",     "#0d2a34",       "#ca4238",     "#88982d",       "#ae8a2c",        "#4689cc",      "#c24380",         "#519e97",      "#fbf6e4",
    "#869395",     "#163540",       "#d2736e",     "#bfcb68",       "#e7c24f",        "#6faee8",      "#db73a7",         "#83d0ca",      "#fbf6e4",
]

SOLARIZED_COLORS_ANSI_TERMINAL_PALETTE = Palette(
    name="Solarized ANSI",
    description="The Solarized dark palette adapted for use in ANSI terminals",
    author="Ulrich Schwenk, based on work by Ethan Schoonover",
    colors=[hex_to_rgb(color) for color in  SOLARIZED_COLORS_ANSI_TERMINAL_HEX],
    color_names=SOLARIZED_COLORS_ANSI_TERMINAL_NAMES,
    color_types=["rgb"] * len(SOLARIZED_COLORS_ANSI_TERMINAL_HEX),
)

