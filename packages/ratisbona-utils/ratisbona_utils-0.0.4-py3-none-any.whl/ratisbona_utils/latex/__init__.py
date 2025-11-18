from .quotes_parser import QuotesParser
from .templates import open_dialogue_document, close_dialogue_document
from .quoting_and_escaping import latex_quote, replace_emojis
from .linebreaks import make_text_to_latex_paragraphs

__all__ = [
    'QuotesParser',
    'open_dialogue_document',
    'close_dialogue_document',
    'latex_quote',
    'replace_emojis'
    'make_text_to_latex_paragraphs'
]