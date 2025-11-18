def safesplit(string: str, splitchar: str = " ", escaping: str = "'\"") -> list:
    """Split string with escaping capabilities.

    Args:
        string (str): The string to parse.
        splitchar (str): The separator.
        ignorechar (str): The character escaping splits.

    Returns:
        list: Splitted string
    """
    if splitchar in escaping:
        msg = "Cannot escape on splitting character !"
        raise ValueError(msg)

    result = []
    buffer = ""
    escape = ""

    for c in string:
        if c in escaping:
            if not escape:
                escape = c
                continue
            if escape == c:
                escape = ""
                continue

        if c == splitchar and not escape:
            if buffer:
                result.append(buffer)
                buffer = ""
            else:
                continue
        else:
            buffer += c

    if buffer:
        result.append(buffer)

    return result
