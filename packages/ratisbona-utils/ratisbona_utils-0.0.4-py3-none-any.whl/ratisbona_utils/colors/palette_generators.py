from functools import partial

import matplotlib

from ratisbona_utils.colors.simple_color import (
    lab_to_rgb,
    cielch_to_lab,
    hsv_to_rgb,
    normalized_to_rgb,
    bounded_or_bust,
)


def cielch_based_rgb_palette(hue_steps: int, lightness, chroma):
    return [
        lab_to_rgb(cielch_to_lab([lightness, chroma, float(i / 10)]))
        for i in range(0, 3600, round(3600 / (hue_steps - 1)))
    ]


def hsv_based_rgb_palette(hue_steps: int, saturation, value):
    return [
        normalized_to_rgb(hsv_to_rgb((float(i / 10), saturation, value)))
        for i in range(0, 3600, round(3600 / (hue_steps - 1)))
    ]


def matplotlib_colormap_to_palette(hue_steps: int, colormap_name: str):
    colormap = matplotlib.colormaps[colormap_name].reversed()
    palette1 = colormap([x / (hue_steps - 1) for x in range(hue_steps)])
    return [normalized_to_rgb((r, g, b)) for r, g, b, a in palette1]





def ega_num_to_rgb(ega: int):
    bounded_or_bust(ega, 0, 63)
    red = 0x55 * (((ega >> 1) & 2) | (ega >> 5) & 1)
    green = 0x55 * ((ega & 2) | (ega >> 4) & 1)
    blue = 0x55 * (((ega << 1) & 2) | (ega >> 3) & 1)
    return red, green, blue


def cga_num_to_normalized_rgb(cga: int):
    bounded_or_bust(cga, 0, 15)
    red = 2 / 3 * (cga & 4) / 4 + 1 / 3 * (cga & 8) / 8
    green = 2 / 3 * (cga & 2) / 2 + 1 / 3 * (cga & 8) / 8
    blue = 2 / 3 * (cga & 1) / 1 + 1 / 3 * (cga & 8) / 8
    if cga == 6:
        green = green * 2 / 3
    return red, green, blue
