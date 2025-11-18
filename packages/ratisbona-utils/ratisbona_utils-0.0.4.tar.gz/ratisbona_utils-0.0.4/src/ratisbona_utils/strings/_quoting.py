def quote_for_bash_double_quotes(
    string: str,
    escape_double_quotes: bool = True,
    escape_backslashes: bool = True,
    escape_dollarsigns: bool = True,
    escape_backticks: bool = True,
    escape_exclamation_marks: bool = True,
) -> str:
    """
    Quote a string for use in bash with double quotes.

    Args:
        string (str): The string to quote.
        escape_double_quotes (bool): Whether to escape double quotes in the string.
        escape_backslashes (bool): Whether to escape backslashes in the string.
        escape_dollarsigns (bool): Whether to escape dollar signs in the string.
        escape_backticks (bool): Whether to escape backticks in the string.
        escape_exclamation_marks (bool): Whether to escape exclamation marks in the string.

    Default:
        All flags true!

    Returns:
        str: The quoted string, einclosed in double quotes.
    """
    if escape_double_quotes:
        string = string.replace('"', '\\"')
    if escape_backslashes:
        string = string.replace('\\', '\\\\')
    if escape_dollarsigns:
        string = string.replace('$', '\\$')
    if escape_backticks:
        string = string.replace('`', '\\`')
    if escape_exclamation_marks:
        string = string.replace('!', '\\!')

    return f'"{string}"'