
import re
from functools import partial
from itertools import pairwise
from typing import Sequence


def snake_to_words(word: str) -> list[str]:
    return list(map(lambda _: _.lower(), word.split('_')))


def words_to_snake(words: Sequence[str]) -> str:
    return '_'.join(map(lambda w: w.lower(), words))


def _camel_or_pascal_to_words(word: str, is_pascal: bool) -> list[str]:
    # Bracketing the matcher in re.split causes the delimiter to become
    # a match group of it's own:
    # a=re.split('(-)', '1-2-3') #=> ['1', '-', '2', '-', '3']
    head, *delimited = re.split(r'([A-Z]+)', word)
    # For Pascal casing (starting with a Uppercase letter, the head must always be an empty group.
    # For Camel casing the head must be filled. Any other combination is an error.
    if is_pascal ^ (head == ''):
        raise ValueError(f'{word}: Thats not {"pascal" if is_pascal else "camel"} casing.')
    words = list(pairwise(delimited))[::2]
    words = map(''.join, words)
    if not is_pascal:
        words = [head, *words]
    words = map(str.lower, words)
    return list(words)


camel_to_words = partial(_camel_or_pascal_to_words, is_pascal=False)

pascal_to_words = partial(_camel_or_pascal_to_words, is_pascal=True)


def words_to_camel(words: Sequence[str]) -> str:
    head, *tail = words
    return ''.join([head, *words_to_pascal(tail)])


def words_to_pascal(words: Sequence[str]) -> str:
    return ''.join(map(lambda w: w.capitalize(), words))