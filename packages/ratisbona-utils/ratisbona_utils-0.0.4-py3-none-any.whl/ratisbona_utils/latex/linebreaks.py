

def make_text_to_latex_paragraphs(text: str) -> str:
    """
    Converts plain text into LaTeX paragraphs by splitting at double newlines.
    Can also be used to remove excessive newlines.

    Args:
        text (str): The input plain text.
    Returns:
        str: The text formatted with LaTeX paragraph breaks.
    """
    paragraphs = text.split("\n")
    latex_paragraphs = [p.strip() for p in paragraphs if p.strip()]
    return "\n\n".join(latex_paragraphs) + "\n"
