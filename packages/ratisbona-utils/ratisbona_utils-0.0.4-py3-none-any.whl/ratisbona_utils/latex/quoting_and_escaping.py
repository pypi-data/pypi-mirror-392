from typing import Callable

_latexSymbols = {
    "%": "\\%",
    "{": "\\{",
    "}": "\\}",
    "_": "\\_",
    "^": "\\^",
    "$": "\\$",
    "#": "\\#",
    "&": "\\&",
    "\\": "\\\\",
    "\u200E": "",  # Unicode Left-to-right selector.
    "\u200D": "",
    "\uFE0F": "",  # Emoticon variant selector
    "\u2642": "\\male{}",
    "\u2641": "\\female{}",
    "\u2640": "\\female{}",
}

_ignoreRanges = [
    (0x2800, 0x28FF),
    (0x200E, 0x200E),
]

'''_emoticon_blocks = [
    (0x1F600, 0x1F64F),
    (0x2600, 0x26FF),
    (0x1F900, 0x1F9FF),
    (0x1F300, 0x1F5FF),
    (0x1F680, 0x1F6FF),
    (0x2700, 0x27BF),
]'''
_emoticon_blocks = [
    (0x2700, 0x27BF),
    (0x1_F000, 0x1_FFFF)
]


def _is_emoji(char: int) -> bool:
    for lower, upper in _emoticon_blocks:
        if lower <= char <= upper:
            return True
    return False

def surround_with_uliji(text: str) -> str:
    return f"\\uliji{{{text}}}"

def replace_emojis(text: str, replacement: Callable[[str], str]=surround_with_uliji) -> str:
    result = ""
    emojis_pending = ""

    for char in text:
        code =  ord(char)

        if _is_emoji(code):
            emojis_pending += char
            continue

        if len(emojis_pending) > 0:
            result += replacement(emojis_pending)
            emojis_pending = ""
        result += char

    if len(emojis_pending) > 0:
        result += replacement(emojis_pending)
    return result


def latex_quote(text: str) -> str:
    result = ""
    for char in text:
        code = ord(char)
        ignore = False
        for the_range in _ignoreRanges:
            if the_range[0] <= code <= the_range[1]:
                print(f"Ignored Charcode: {code:x}")
                ignore = True
                break
        if ignore:
            continue

        if char in _latexSymbols:
            result += _latexSymbols[char]
            continue

        if ord(char) == 0x200E:
            raise ValueError(text)

        result += char
    return result