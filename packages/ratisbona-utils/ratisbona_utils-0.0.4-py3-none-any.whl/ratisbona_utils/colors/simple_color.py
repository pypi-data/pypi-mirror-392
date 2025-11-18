import math
from functools import partial
from typing import TypeVar, Callable

T = TypeVar("T", float, int)


def bounded(value: T, lower_bound: T, upper_bound: T) -> T:
    """
    Bound a value between a lower and upper bound. If value is not within bounds, it is set to the closest bound.

    Args:
        value: The value to bound
        lower_bound: The lower bound
        upper_bound: The upper bound

    Returns:
        value if it is within bounds, otherwise the closest bound.
    """
    if value < lower_bound:
        return lower_bound
    if value > upper_bound:
        return upper_bound
    return value


def bounded_or_bust(value: T, lower_bound: T, upper_bound: T) -> T:
    """
    Bound a value between a lower and upper bound. If value is not within bounds, a ValueError is raised.

    Args:
        value: The value to bound
        lower_bound: The lower bound
        upper_bound: The upper bound

    Returns:
        The bounded value

    Raises:
        ValueError: If the value is not within bounds
    """
    if value < lower_bound:
        raise ValueError(f"Value {value} is less than lower bound {lower_bound}")
    if value > upper_bound:
        raise ValueError(f"Value {value} is greater than upper bound {upper_bound}")
    return value


RGBComponent = int
""" A component of an RGB color."""


def rgb_bounding(value: RGBComponent) -> RGBComponent:
    """
    Curried bounded to bound an RGB component between 0 and 255.

    Args:
        value: The value to bound

    Returns:
        The bounded value
    """
    return bounded(value, 0, 255)


rgb_or_bust = partial(bounded_or_bust, lower_bound=0, upper_bound=255)
""" Bound an RGB component between 0 and 255, raising a ValueError if it is not within bounds. """

RGBColor = tuple[RGBComponent, RGBComponent, RGBComponent]
"""
    An RGB color. An RgbColor is a tuple of three RGB components, values between 0 and 255 (one byte).
    The first component is the red component, the second is the green component, and the third is the blue component.
    RGBColors are not with respect to any color space, and are not linearized. What you get is in relation to on what your
    device thinks is 100% red, green, and blue.
"""

NormalizedRGBComponent = float
""" A component of a normalized RGB color. """

normalized_rgb_bounding = partial(bounded, lower_bound=0.0, upper_bound=1.0)
""" Bound a normalized RGB component between 0 and 1. """

normalized_rgb_or_bust = partial(bounded_or_bust, lower_bound=0.0, upper_bound=1.0)
""" Bound a normalized RGB component between 0 and 1, raising a ValueError if it is not within bounds. """

NormalizedRGBColor = tuple[
    NormalizedRGBComponent, NormalizedRGBComponent, NormalizedRGBComponent
]
"""
    A normalized RGB color. A NormalizedRgbColor is a tuple of three normalized RGB components, values between 0 and 1.
    The first component is the red component, the second is the green component, and the third is the blue component.
    Normalized colors are not linearized and to not refer to a specific colorspace. They are just normalized to be between 0 and 1.
"""

LinearizedsRGBComponent = float
""" A component of a linearized sRGB color. A linearized sRGB component is a float between 0 and 1. """
linearized_srgb_bounding = partial(bounded, lower_bound=0.0, upper_bound=1.0)
""" Bound a linearized sRGB component between 0 and 1. """
linearized_srgb_or_bust = partial(bounded_or_bust, lower_bound=0.0, upper_bound=1.0)
""" Bound a linearized sRGB component between 0 and 1, raising a ValueError if it is not within bounds. """
LinearizedsRGBColor = tuple[
    LinearizedsRGBComponent, LinearizedsRGBComponent, LinearizedsRGBComponent
]
""" 
    A linearized sRGB color. A LinearizedsRGBColor is a tuple of three linearized sRGB components, 
    values between 0 and 1. The order again is red, green and blue.
    Linearized sRGB components are linearized from the gamma corrected sRGB components, they refer to the
    sRGB color space as defined by Adobe and Messysoft.
"""

XYZComponent = float
""" A component of a CIE XYZ color. A CIE XYZ component is a float between 0 and 1. """
uxyz_bounding = partial(bounded, lower_bound=0.0, upper_bound=1.0)
""" Bound a CIE XYZ component between 0 and 1. uxyz here stands for upper-case XYZ."""
uxyz_or_bust = partial(bounded_or_bust, lower_bound=0.0, upper_bound=1.0)
""" Bound a CIE XYZ component between 0 and 1, raising a ValueError if it is not within bounds. uxyz here stands for upper-case XYZ."""
XYZColor = tuple[XYZComponent, XYZComponent, XYZComponent]
""" A CIE XYZ color. A XYZColor is a tuple of three CIE XYZ components, values between 0 and 1. The order is X, Y, Z. """

LabLComponent = float
""" A component of a CIE Lab color. A CIE Lab L component is a float between 0 and 100. It represents the lightness of the color. """
lab_l_bounding = partial(bounded, lower_bound=0.0, upper_bound=100.0)
""" Bound a CIE Lab L component between 0 and 100. """
lab_l_or_bust = partial(bounded_or_bust, lower_bound=0.0, upper_bound=100.0)
""" Bound a CIE Lab L component between 0 and 100, raising a ValueError if it is not within bounds. """
LababComponent = float
""" A component of a CIE Lab color. A CIE Lab a or b component is a float between -128 and 127. They represent the hue of the color,
whereby a is the green-red axis and b is the blue-yellow axis. """
lab_ab_bounding = partial(bounded, lower_bound=-128.0, upper_bound=127.0)
""" Bound a CIE Lab a or b component between -128 and 127. """
lab_ab_or_bust = partial(bounded_or_bust, lower_bound=-128.0, upper_bound=127.0)
""" 
    Bound a CIE Lab a or b component between -128 and 127, raising a ValueError 
    if it is not within bounds. 
"""

LabColor = tuple[LabLComponent, LababComponent, LababComponent]
"""
    A CIE Lab color. A LabColor is a tuple of three CIE Lab components, 
    the first is the lightness, the second is the a component, and the third is the b component.
"""

HexColor = str
"""
    A seven char representation of a color. The format is a literal # and then six hexadecimal characters 
    in the format RRGGBB. Hexadecimal Digits are 0-9 and A-F. Upper case letters should be used, but parsing 
    routines must not be case-sensitive.
"""

to_int_16 = partial(int, base=16)


def hex_to_rgb(hex_color: HexColor) -> RGBColor:
    """
    Convert a hexadecimal color to an RGB color.

    Args:
        hex_color: The hexadecimal color to convert

    Returns:
        The RGB color
    """
    if len(hex_color) != 7 or hex_color[0] != "#":
        raise ValueError(f"Invalid hex color: {hex_color}")

    hex_string = hex_color.upper()
    sr, sg, sb = hex_string[1:3], hex_string[3:5], hex_string[5:7]
    r, g, b = map(to_int_16, (sr, sg, sb))
    return r, g, b


def rgb_to_hex(rgb: RGBColor) -> HexColor:
    """
    Convert an RGB color to a hexadecimal color.

    Args:
        rgb: The RGB color to convert

    Returns:
        The hexadecimal color
    """
    r, g, b = map(lambda c: f"{c:02X}", rgb)
    return f"#{r}{g}{b}"


def rgb_to_normalized_component(rgb: RGBComponent) -> NormalizedRGBComponent:
    """
    Convert an RGB component to a normalized RGB component.

    Args:
        rgb: The RGB component to convert

    Returns:
        The normalized RGB component
    """
    return bounded(rgb / 255, 0.0, 1.0)


def normalized_to_rgb_component(normalized: NormalizedRGBComponent) -> RGBComponent:
    """
    Convert a normalized RGB component (between 0 and 1) to an RGB component (between 0 and 255).

    Args:
        normalized: The normalized RGB component to convert (between 0 and 1)

    Returns:
        The RGB component (between 0 and 255)
    """
    return int(bounded(int(normalized * 255), 0, 255))


def rgb_to_normalized(rgb: RGBColor) -> NormalizedRGBColor:
    """
    Convert an RGB color to a normalized RGB color.

    Note:
        That normalization is not linearization. The RGB color is just normalized to be between 0 and 1.
        If you need linearization, you need to convert the RGB color to a linearized sRGB color, for example
        by using the `normalized_to_linearized` function.

    Args:
        rgb: The RGB color to convert

    Returns:
        The normalized RGB color
    """
    nr, ng, nb = map(rgb_to_normalized_component, rgb)
    return nr, ng, nb


def normalized_to_rgb(normalized_rgb: NormalizedRGBColor) -> RGBColor:
    """
    Convert a normalized RGB color to an RGB color.

    Args:
        normalized_rgb: The normalized RGB color to convert

    Returns:
        The RGB color
    """
    r, g, b = map(normalized_to_rgb_component, normalized_rgb)
    return r, g, b


def gamma_function(
    normalized_rgb_component: NormalizedRGBComponent,
) -> LinearizedsRGBComponent:
    """
    Apply the gamma function to a normalized RGB component to linearize it.

    Args:
        normalized_rgb_component: The normalized RGB component to linearize

    Returns:
        The linearized sRGB component
    """
    if normalized_rgb_component <= 0.04045:
        return normalized_rgb_component / 12.92
    return ((normalized_rgb_component + 0.055) / 1.055) ** 2.4


def inverse_gamma_function(
    linearized_rgb_component: LinearizedsRGBComponent,
) -> LinearizedsRGBComponent:
    """
    Apply the inverse gamma function to a linearized sRGB component to gamma correct it.

    Args:
        linearized_rgb_component: The linearized sRGB component to gamma correct

    Returns:
        The gamma corrected sRGB component
    """
    if linearized_rgb_component <= 0.0031308:
        return 12.92 * linearized_rgb_component
    return 1.055 * (linearized_rgb_component ** (1 / 2.4)) - 0.055


def normalized_to_linearized(normalized_rgb: NormalizedRGBColor) -> LinearizedsRGBColor:
    """
    Convert a normalized RGB color to a linearized sRGB color.

    Args:
        normalized_rgb: The normalized RGB color to convert

    Returns:
        The linearized sRGB color
    """
    r, g, b = map(gamma_function, normalized_rgb)
    r, g, b = map(linearized_srgb_bounding, (r, g, b))
    return r, g, b


def linearized_to_normalized(linearized_rgb: LinearizedsRGBColor) -> NormalizedRGBColor:
    """
    Convert a linearized sRGB color to a normalized RGB color.
    Args:
        linearized_rgb: the linearized sRGB color to convert

    Returns:
        The normalized RGB color

    """
    r, g, b = map(inverse_gamma_function, linearized_rgb)
    r, g, b = map(normalized_rgb_bounding, (r, g, b))
    return r, g, b


def add_colors(
    one: tuple[T, T, T], two: tuple[T, T, T], bounding_function: Callable[[T], T] = lambda x: x
) -> tuple[T, T, T]:
    """
    Add two colors together. The colors are bounded by the bounding function, so
    adding 100% red to 100% does not give 200% red, but 100% red.

    Args:
        one: The first color to add
        two: The second color to add
        bounding_function: The function to bound the result

    Returns:
        The sum of the two colors

    """
    one, two, three = (bounding_function(a + b) for a, b in zip(one, two))
    return one, two, three


add_rgb_colors = partial(add_colors, bounding_function=rgb_bounding)
""" 
    Add two RGB colors together.
    
    Args:
        one: The first color to add
        two: The second color to add
        
    Returns:
        The sum of the two colors 
"""

add_normalized_rgb_colors = partial(
    add_colors, bounding_function=normalized_rgb_bounding
)
""" 
    Add two normalized RGB colors together.
    
    Args:
        one: The first color to add
        two: The second color to add
        
    Returns:
        The sum of the two colors 
"""

add_linearized_srgb_colors = partial(
    add_colors, bounding_function=linearized_srgb_bounding
)
""" 
    Add two linearized sRGB colors together.
    
    Args:
        one: The first color to add
        two: The second color to add
        
    Returns:
        The sum of the two colors
"""


def multiply_color(
    color: tuple[T, T, T], number: float, bounding_function: Callable[[T], T]
) -> tuple[T, T, T]:
    """
    Multiply a color by a number. The color is bounded by the bounding function, so
    Args:
        color: The color to multiply
        number: A number to multiply the color with
        bounding_function: The function to bound the result

    Returns:
        The color multiplied by the number.
    """
    one, two, three = (bounding_function(component * number) for component in color)
    return one, two, three


multiply_rgb_color = partial(multiply_color, bounding_function=rgb_bounding)
"""
    Multiply an RGB color by a number.
    
    Args:
        color: The color to multiply
        number: A number to multiply the color with
        
    Returns:
        The color multiplied by the number.
"""
multiply_normalized_rgb_color = partial(
    multiply_color, bounding_function=normalized_rgb_bounding
)
"""
    Multiply a normalized RGB color by a number.
    
    Args:
        color: The color to multiply
        number: A number to multiply the color with
        
    Returns:
        The color multiplied by the number.
        
"""

multiply_linearized_srgb_color = partial(
    multiply_color, bounding_function=linearized_srgb_bounding
)
"""
    Multiply a linearized sRGB color by a number.
    
    Args:
        color: The color to multiply
        number: A number to multiply the color with
        
    Returns:
        The color multiplied by the number.
"""


def linear_blend(
    color1: tuple[T, T, T],
    color2: tuple[T, T, T],
    alpha: float,
    bounding_function: Callable[[T], T],
) -> tuple[T, T, T]:
    """
    Linearly blend two colors together. The alpha value determines the weight of the two colors.

    Args:
        color1: The first color to blend
        color2:  The second color to blend
        alpha:  The alpha value, a float between 0 and 1
        bounding_function:  The function to bound the result

    Returns:
        The linearly blended color
    """
    if not 0 <= alpha <= 1:
        raise ValueError(f"Invalid alpha value: {alpha}")
    return add_colors(
        multiply_color(color1, 1 - alpha, bounding_function),
        multiply_color(color2, alpha, bounding_function),
        bounding_function,
    )


linear_blend_rgb = partial(linear_blend, bounding_function=rgb_bounding)
"""
    Linearly blend two RGB colors together. The alpha value determines the weight of the two colors.
    
    Args:
        color1: The first color to blend 
        color2:  The second color to blend
        alpha:  The alpha value, a float between 0 and 1
        
    Returns:
        The linearly blended color
"""

HSVHComponent = float
""" A component of an HSV color. The hue component is a float between 0 and 360. """


def hsv_h_bounding(value: float) -> float:
    """
    Bound an HSV hue component between 0 and 360.

    Args:
        value: The value to bound

    Returns:
        The bounded value
    """
    return value % 360  # yeah that also works for negative values


HSVSVComponent = float
""" A component of an HSV color. The saturation and value components are floats between 0 and 1. """

hsv_sv_bounding = partial(bounded, lower_bound=0.0, upper_bound=1.0)
HSVColor = tuple[HSVHComponent, HSVSVComponent, HSVSVComponent]


def rgb_to_hsv(rgb: NormalizedRGBColor) -> HSVColor:
    """
    Convert an RGB color to an HSV color.

    Args:
        rgb: The RGB color to convert

    Returns:
        The HSV color
    """
    cmax = max(rgb)
    cmin = min(rgb)
    r, g, b = rgb
    delta = cmax - cmin
    if delta == 0:
        h = 0
    elif cmax == r:
        h = 60 * (((g - b) / delta) % 6)
    elif cmax == g:
        h = 60 * ((b - r) / delta + 2)
    else:
        h = 60 * ((r - g) / delta + 4)

    s = 0 if cmax == 0 else delta / cmax
    v = cmax
    return hsv_h_bounding(h), hsv_sv_bounding(s), hsv_sv_bounding(v)


def hsv_to_rgb(hsv: HSVColor) -> NormalizedRGBColor:
    """
    Convert an HSV color to an RGB color.

    Args:
        hsv: The HSV color to convert

    Returns:
        The RGB color
    """
    h, s, v = hsv
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return r + m, g + m, b + m


def srgb_linearized_to_uxyz(rgb_01: LinearizedsRGBColor) -> XYZColor:
    """
    Convert a linearized sRGB color to a CIE XYZ color.

    Args:
        rgb_01: The linearized sRGB color to convert

    Returns:
        The CIE XYZ color
    """
    r, g, b = rgb_01
    ux = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    uy = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    uz = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    ux, uy, uz = map(uxyz_bounding, (ux, uy, uz))
    return ux, uy, uz


def uxyz_color_to_linearized_srgb_color(uxyz: XYZColor) -> LinearizedsRGBColor:
    """
    Convert a CIE XYZ color to a linearized sRGB color.

    Args:
        uxyz: The CIE XYZ color to convert

    Returns:
        The linearized sRGB color
    """
    ux, uy, uz = uxyz
    r = ux * 3.2404542 + uy * -1.5371385 + uz * -0.4985314
    g = ux * -0.9692660 + uy * 1.8760108 + uz * 0.0415560
    b = ux * 0.0556434 + uy * -0.2040259 + uz * 1.0572252
    r, g, b = map(linearized_srgb_bounding, (r, g, b))
    return r, g, b


D50_XYZ_2deg = 0.96422, 1.0, 0.82521
""" The CIE XYZ color of the D50 white point for 2 degree observer. """

D65_XYZ_2deg = 0.95047, 1.0, 1.08883
""" The CIE XYZ color of the D65 white point for 2 degree observer. """

D50_XYZ_10deg = 0.967206, 1.0, 0.814280
""" The CIE XYZ color of the D50 white point for 10 degree observer. """

D65_XYZ_10deg = 0.948109, 1.0, 1.073043
""" The CIE XYZ color of the D65 white point for 10 degree observer. """


def linearize_uxyz_color_relative_to_whitepoint(
    uxyz: XYZColor, white_point: XYZColor
) -> XYZColor:
    """
    Linearize a CIE XYZ color relative to a white point. This is useful for color matching and color correction.
    Args:
        uxyz:  The CIE XYZ color to linearize
        white_point:  The white point to linearize the color relative to

    Returns:
        The linearized CIE XYZ color
    """
    ux, uy, uz = uxyz
    uxn, uyn, uzn = white_point
    ux, uy, uz = ux / uxn, uy / uyn, uz / uzn
    ux, uy, uz = map(uxyz_bounding, (ux, uy, uz))
    return ux, uy, uz


def delinearize_uxyz_color_relative_to_whitepoint(
    uxyz: XYZColor, white_point: XYZColor
) -> XYZColor:
    """
    Delinearize a CIE XYZ color relative to a white point. This is useful for color matching and color correction.

    Args:
        uxyz: The CIE XYZ color to delinearize
        white_point: The white point to delinearize the color relative to

    Returns:
        The delinearized CIE XYZ color
    """
    ux, uy, uz = uxyz
    uxn, uyn, uzn = white_point
    ux, uy, uz = ux * uxn, uy * uyn, uz * uzn
    ux, uy, uz = map(uxyz_bounding, (ux, uy, uz))
    return ux, uy, uz


def f(t: float) -> float:
    """
    The f function used in the CIE Lab color space which is used to linearize the lightness.

    Args:
        t: The value to apply the function to

    Returns:
        The result of the function
    """
    if t > 216 / 24389:
        return t ** (1 / 3)
    return 841 / 108 * t + 4 / 29


def f_inv(t: float) -> float:
    """
    The inverse of the f function used in the CIE Lab color space.
    Args:
        t:  The value to apply the inverse function to

    Returns:
        The result of the inverse function
    """
    if t > 6 / 29:
        return t**3
    return 108 / 841 * (t - 4 / 29)


def uxyz_color_to_lab_color(uxyz_linearized_to_light: XYZColor) -> LabColor:
    """
    Convert a CIE XYZ color to a CIE Lab color.
    Args:
        uxyz_linearized_to_light:  The CIE XYZ color to convert

    Returns:
        The CIE Lab color
    """
    ux, uy, uz = uxyz_linearized_to_light
    ul = 116 * f(uy) - 16
    a = 500 * (f(ux) - f(uy))
    b = 200 * (f(uy) - f(uz))
    ul = lab_l_bounding(ul)
    a, b = map(lab_ab_bounding, (a, b))
    return ul, a, b


def lab_color_to_uxyz_color(lab: LabColor) -> XYZColor:
    """
    Convert a CIE Lab color to a CIE XYZ color.

    Args:
        lab: The CIE Lab color to convert

    Returns:
        The CIE XYZ color
    """
    ul, a, b = lab
    uy = (ul + 16) / 116
    ux = uy + a / 500
    uz = uy - b / 200
    ux, uy, uz = map(uxyz_bounding, map(f_inv, (ux, uy, uz)))
    return ux, uy, uz


def rgb_to_lab(rgb: RGBColor, whitepoint: XYZColor = D65_XYZ_10deg) -> LabColor:
    """
    Convert an RGB color to a CIE Lab color.
    Args:
        rgb:  The RGB color to convert
        whitepoint:  The white point to convert the color relative to

    Returns:
        The CIE Lab color
    """
    nrgb = rgb_to_normalized(rgb)
    srgb = normalized_to_linearized(nrgb)
    uxyz = srgb_linearized_to_uxyz(srgb)
    xyz = linearize_uxyz_color_relative_to_whitepoint(uxyz, whitepoint)
    lab = uxyz_color_to_lab_color(xyz)
    return lab

def lab_lighten_rgb(rgb: RGBColor, lightness_increment: float, whitepoint: XYZColor = D65_XYZ_10deg) -> RGBColor:
    lab_color = rgb_to_lab(rgb, whitepoint)
    lightened = add_colors(lab_color, (lightness_increment, 0, 0))
    return lab_to_rgb(lightened, whitepoint)

def lab_to_rgb(lab: LabColor, whitepoint: XYZColor = D65_XYZ_10deg) -> RGBColor:
    """
    Convert a CIE Lab color to an RGB color.
    Args:
        lab:  The CIE Lab color to convert
        whitepoint: The white point to convert the color relative to

    Returns:
        The RGB color
    """
    xyz = lab_color_to_uxyz_color(lab)
    uxyz = delinearize_uxyz_color_relative_to_whitepoint(xyz, whitepoint)
    srgb = uxyz_color_to_linearized_srgb_color(uxyz)
    nrgb = linearized_to_normalized(srgb)
    rgb = normalized_to_rgb(nrgb)
    return rgb


CIELCHColor = tuple[LabLComponent, float, float]


def lab_to_cielch(lab: LabColor) -> CIELCHColor:
    """
    Convert a CIE Lab color to a CIE LCH color.

    Args:
        lab: The CIE Lab color to convert

    Returns:
        The CIE LCH color
    """
    l, a, b = lab
    c = (a**2 + b**2) ** 0.5
    h = math.degrees(math.atan2(b, a))
    if h < 0:
        h += 360
    return l, c, h


def cielch_to_lab(cielch: CIELCHColor) -> LabColor:
    """
    Convert a CIE LCH color to a CIE Lab color.

    Args:
        cielch: The CIE LCH color to convert

    Returns:
        The CIE Lab color
    """
    l, c, h = cielch
    a = c * math.cos(math.radians(h))
    b = c * math.sin(math.radians(h))
    return l, a, b

LMSComponent = float
""" A component of an LMS color. """

LMSColor = tuple[LMSComponent, LMSComponent, LMSComponent]
""" A color in the LMS color space. """

def uxyz_color_to_lms_color(uxyz_color: XYZColor) -> LMSColor:
    x, y, z = uxyz_color
    l =  0.4002 * x + 0.7076 * y - 0.0808 * z
    m = -0.2263 * x + 1.1653 * y + 0.0457 * z
    s =                          + 0.9182 * z
    return l, m, s

def lms_color_to_uxyz_color(lms_color: LMSColor) -> XYZColor:
    l, m, s = lms_color
    x = 1.86006661  * l - 1.12948008  * m + 0.219898303  * s
    y = 0.361222925 * l + 0.638804306 * m - 0.0000071275 * s
    z =                                   + 1.0890873    * s
    return x, y, z

def lms_colorblindness_p(lms_color: LMSColor) -> LMSColor:
    l, m, s = lms_color
    L = 1.05118294 * m - 0.05116099 * s
    return L, m, s

def lms_colorblindness_d(lms_color: LMSColor) -> LMSColor:
    l, m, s = lms_color
    M = 0.9513092 * l + 0.04866992 * s
    return l, M, s

def lms_colorblindness_t(lms_color: LMSColor) -> LMSColor:
    l, m, s = lms_color
    S = -0.86744736 * l + 1.86727089 * m
    return l, m, S


def rgb_to_colorblindness(rgb: RGBColor, blindness: Callable[[LMSColor], LMSColor] = lms_colorblindness_t) -> RGBColor:
    """
    Function simulating color blindness via the lms-colorspace.

    Args:
        rgb: An RGB color.
        blindness: A colorblindness mapping function. Use lms_colorblindness_p, lms_colorblindness_d or lms_colorblindness_t for example.

    Returns:
        The RGB color after applying the color blindness mapping.

    """
    nrgb = rgb_to_normalized(rgb)
    srgb = normalized_to_linearized(nrgb)
    uxyz = srgb_linearized_to_uxyz(srgb)
    lms = uxyz_color_to_lms_color(uxyz)
    blind_lms = blindness(lms)
    uxyz = lms_color_to_uxyz_color(blind_lms)
    srgb = uxyz_color_to_linearized_srgb_color(uxyz)
    nrgb = linearized_to_normalized(srgb)
    rgb = normalized_to_rgb(nrgb)
    return rgb