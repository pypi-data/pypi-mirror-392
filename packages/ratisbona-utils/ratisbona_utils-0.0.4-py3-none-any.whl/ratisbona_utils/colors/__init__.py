"""
    This module provides a set of classes and functions to work with colors.
    It can handle the following color spaces: RGB, normalized RGB,
    linearized sRGB, XYZ, Lab, and hexadecimal.
    It also provides functions to convert between these color spaces.
    It also provides functions to interpolate between colors.
    It also provides functions to add colors.
    It also provides functions to blend colors.
"""

from . import resources
from .serde_gimp import to_gimp_palette, parse_gimp_palette, to_gimp_gradient
from .palette import Palette, linear_interpolate, linear_interpolate_two_colors
from .simple_color import (
    RGBComponent,
    RGBColor,
    NormalizedRGBComponent,
    NormalizedRGBColor,
    LinearizedsRGBComponent,
    LinearizedsRGBColor,
    XYZComponent,
    XYZColor,
    LabLComponent,
    LababComponent,
    LabColor,
    HexColor,
    hex_to_rgb,
    rgb_to_hex,
    rgb_to_normalized_component,
    normalized_to_rgb_component,
    rgb_to_normalized,
    normalized_to_rgb,
    gamma_function,
    inverse_gamma_function,
    normalized_to_linearized,
    linearized_to_normalized,
    add_colors,
    add_rgb_colors,
    add_normalized_rgb_colors,
    add_linearized_srgb_colors,
    multiply_color,
    multiply_normalized_rgb_color,
    multiply_linearized_srgb_color,
    linear_blend,
    linear_blend_rgb,
    srgb_linearized_to_uxyz,
    uxyz_color_to_linearized_srgb_color,
    D50_XYZ_2deg,
    D65_XYZ_10deg,
    D50_XYZ_10deg,
    D65_XYZ_2deg,
    linearize_uxyz_color_relative_to_whitepoint,
    delinearize_uxyz_color_relative_to_whitepoint,
    uxyz_color_to_lab_color,
    lab_color_to_uxyz_color,
    rgb_to_lab,
    lab_to_rgb,
)
