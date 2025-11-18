from dataclasses import dataclass
from enum import Enum

from ratisbona_utils.strings import align, longest_line, Alignment
from ratisbona_utils.terminals.vt100 import color_text


class LineStyle(Enum):
    SINGLE = 0, [0, 0, 0]
    SINGLE_HEAVY = 1, [1, 0, 0]
    DOUBLE = 2, [2, 2, 0]
    TWO_DASH = 3, [0, 0, 0]
    TWO_DASH_HEAVY = 4, [1, 0, 0]
    THREE_DASH = 5, [0, 0, 0]
    THREE_DASH_HEAVY = 6, [1, 0, 0]
    FOUR_DASH = 7, [0, 0, 0]
    FOUR_DASH_HEAVY = 8, [1, 0, 0]

    def __init__(self, value, replacement_escalations: list[int]):
        super().__init__(value)
        self.intvalue = value
        self.replacement_escalations = replacement_escalations


LINESTYLE_BY_REPLACEMENT = {style.intvalue: style for style in LineStyle}


@dataclass(frozen=True)
class BoxCellDescription:
    top: LineStyle | None
    right: LineStyle | None
    bottom: LineStyle | None
    left: LineStyle | None


def _create_dictionary():
    s = LineStyle.SINGLE
    h = LineStyle.SINGLE_HEAVY
    d2 = LineStyle.TWO_DASH
    d2h = LineStyle.TWO_DASH_HEAVY
    d3 = LineStyle.THREE_DASH
    d3h = LineStyle.THREE_DASH_HEAVY
    d4 = LineStyle.FOUR_DASH
    d4h = LineStyle.FOUR_DASH_HEAVY
    d = LineStyle.DOUBLE
    _ = None

    retval = {}

    def bd(
        top: LineStyle | None,
        right: LineStyle | None,
        bottom: LineStyle | None,
        left: LineStyle | None,
        char: int,
    ):
        retval[BoxCellDescription(top, right, bottom, left)] = char

    bd(_, s, _, s, 0x2500),  # --
    bd(_, h, _, h, 0x2501),
    bd(s, _, s, _, 0x2502),  # |
    bd(h, _, h, _, 0x2503),
    bd(_, d3, _, d3, 0x2504),  # --
    bd(_, d3h, _, d3h, 0x2505),
    bd(d3, _, d3, _, 0x2506),  # |
    bd(d3h, _, d3h, _, 0x2507),

    bd(_, d4, _, d4, 0x2508),  # --
    bd(_, d4h, _, d4h, 0x2509),

    bd(d4, _, d4, _, 0x250A),  # |
    bd(d4h, _, d4h, _, 0x250B),

    bd(_, s, s, _, 0x250C),  # ,-
    bd(_, h, s, _, 0x250D),
    bd(_, s, h, _, 0x250E),
    bd(_, h, h, _, 0x250F),

    bd(_, _, s, s, 0x2510),  # -,
    bd(_, _, h, s, 0x2511),
    bd(_, _, s, h, 0x2512),
    bd(_, _, h, h, 0x2513),

    bd(s, s, _, _, 0x2514),  # '-,
    bd(s, h, _, _, 0x2515),
    bd(h, s, _, _, 0x2516),
    bd(h, h, _, _, 0x2517),

    bd(s, _, _, s, 0x2518),  # -'
    bd(s, _, _, h, 0x2519),
    bd(h, _, _, s, 0x251A),
    bd(h, _, _, h, 0x251B),

    bd(s, s, s, _, 0x251C),  # |-
    bd(s, h, s, _, 0x251D),
    bd(h, s, s, _, 0x251E),
    bd(s, s, h, _, 0x251F),
    bd(h, s, h, _, 0x2520),
    bd(h, h, s, _, 0x2521),
    bd(s, h, h, _, 0x2522),
    bd(h, h, h, _, 0x2523),

    bd(s, _, s, s, 0x2524),  # -|
    bd(s, _, s, h, 0x2525),
    bd(h, _, s, s, 0x2526),
    bd(s, _, s, h, 0x2527),
    bd(h, _, h, s, 0x2528),
    bd(h, _, s, h, 0x2529),
    bd(s, _, h, h, 0x252A),
    bd(h, _, h, h, 0x252B),

    bd(_, s, s, s, 0x252C),  # -,-
    bd(_, s, s, h, 0x252D),
    bd(_, h, s, s, 0x252E),
    bd(_, h, s, h, 0x252F),
    bd(_, s, h, s, 0x2530),
    bd(_, s, h, h, 0x2531),
    bd(_, h, h, s, 0x2532),
    bd(_, h, h, h, 0x2533),

    bd(s, s, _, s, 0x2534),  # -`-
    bd(s, h, _, s, 0x2535),
    bd(h, s, _, s, 0x2536),
    bd(s, h, _, h, 0x2537),
    bd(h, s, _, s, 0x2538),
    bd(h, s, _, h, 0x2539),
    bd(h, h, _, s, 0x253A),
    bd(h, h, _, h, 0x253B),

    bd(s, s, s, s, 0x253C),  #  +
    bd(s, s, s, h, 0x253D),
    bd(s, h, s, s, 0x253E),
    bd(s, h, s, h, 0x253F),
    bd(h, s, s, s, 0x2540),
    bd(s, s, h, s, 0x2541),
    bd(h, s, h, s, 0x2542),
    bd(h, s, s, h, 0x2543),
    bd(h, h, s, s, 0x2544),
    bd(s, s, h, h, 0x2545),
    bd(s, h, h, s, 0x2546),
    bd(h, h, s, h, 0x2547),
    bd(s, h, h, h, 0x2548),
    bd(h, s, h, h, 0x2549),
    bd(h, h, h, s, 0x254A),
    bd(h, h, h, h, 0x254B),

    bd(_, d2, d2, _, 0x254C),  #  -
    bd(_, d2h, d2h, _, 0x254D),
    bd(d2, _, _, d2, 0x254E),
    bd(d2h, _, _, d2h, 0x254F),

    bd(_, d, _, d, 0x2550),  #  ==
    bd(d, _, d, _, 0x2551),  #  ||
    bd(_, d, s, _, 0x2552),  #  ,=
    bd(_, s, d, _, 0x2553),  # ,,-
    bd(_, d, d, _, 0x2554),  #  ,,=
    bd(_, _, s, d, 0x2555),  #  =,
    bd(_, _, d, s, 0x2556),  #  -,,
    bd(_, _, d, d, 0x2557),  #  =,,
    bd(s, d, _, _, 0x2558),  #  '=
    bd(d, s, _, _, 0x2559),  #  ,,-
    bd(d, d, _, _, 0x255A),  #  ,,=
    bd(s, _, _, d, 0x255B),  #  =''
    bd(d, _, _, s, 0x255C),  #  =''
    bd(d, _, _, d, 0x255D),  #  =''
    bd(s, d, s, _, 0x255E),  #  |=
    bd(d, s, d, _, 0x255F),  #  ||-
    bd(d, d, d, _, 0x2560),  #  ||=
    bd(s, _, s, d, 0x2561),  #  =|
    bd(d, _, d, s, 0x2562),  #  -||
    bd(d, _, d, d, 0x2563),  #  =||
    bd(_, s, d, s, 0x2564),  #  -,,-
    bd(_, d, s, d, 0x2565),  #  =,=
    bd(_, d, d, d, 0x2566),  #  =,,=
    bd(s, d, _, d, 0x2567),  #  ='=
    bd(d, s, _, s, 0x2568),  #  -''-
    bd(d, d, _, d, 0x2569),  #  =''=
    bd(s, d, s, d, 0x256A),  #  =|=
    bd(d, s, d, s, 0x256B),  #  -||-
    bd(d, d, d, d, 0x256C),  #  =||=
    return retval


DESCRIPTIONS = _create_dictionary()


def get_char(description: BoxCellDescription) -> str:
    if description in DESCRIPTIONS:
        return chr(DESCRIPTIONS[description])
    for escalation in range(3):
        alternate_description = BoxCellDescription(
            (
                LINESTYLE_BY_REPLACEMENT[
                    description.top.replacement_escalations[escalation]
                ]
                if description.top is not None
                else None
            ),
            (
                LINESTYLE_BY_REPLACEMENT[
                    description.right.replacement_escalations[escalation]
                ]
                if description.right is not None
                else None
            ),
            (
                LINESTYLE_BY_REPLACEMENT[
                    description.bottom.replacement_escalations[escalation]
                ]
                if description.bottom is not None
                else None
            ),
            (
                LINESTYLE_BY_REPLACEMENT[
                    description.left.replacement_escalations[escalation]
                ]
                if description.left is not None
                else None
            ),
        )
        if alternate_description in DESCRIPTIONS:
            return chr(DESCRIPTIONS[alternate_description])
    return "*"


def draw_box(
    multiline_text: str,
    linestyle: LineStyle | str = LineStyle.SINGLE,
    alignment: Alignment = Alignment.LEFT,
    width=None,
) -> str:
    effective_width = width or longest_line(multiline_text) + 4

    if isinstance(linestyle, str):
        vertical = linestyle
        horizontal = linestyle
        top_left = linestyle
        top_right = linestyle
        bottom_left = linestyle
        bottom_right = linestyle
    else:
        vertical = get_char(BoxCellDescription(linestyle, None, linestyle, None))
        horizontal = get_char(BoxCellDescription(None, linestyle, None, linestyle))
        top_left = get_char(BoxCellDescription(None, linestyle, linestyle, None))
        top_right = get_char(BoxCellDescription(None, None, linestyle, linestyle))
        bottom_left = get_char(BoxCellDescription(linestyle, linestyle, None, None))
        bottom_right = get_char(BoxCellDescription(linestyle, None, None, linestyle))

    result = ""
    result += top_left + horizontal * (effective_width - 2) + top_right + "\n"
    for line in multiline_text.splitlines():
        result += vertical
        result += " "
        result += align(line, width=effective_width - 3, alignment=alignment)
        result += vertical
        result += "\n"
    result += bottom_left + horizontal * (effective_width - 2) + bottom_right + "\n"
    return result

def blue_dosbox(text: str) -> str:
    box = draw_box(text, width=80, alignment=Alignment.CENTER, linestyle=LineStyle.DOUBLE)
    return color_text(box, background=(0, 0, 128), foreground=(255, 255, 255))

