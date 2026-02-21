def add_line(line, comment=None, line_length=54):
    """Add a line to the script with an optional comment, aligned to the right.

    Parameters
    ----------
    line : str
        The line to add to the script.
    comment : str, optional
        An optional comment to add to the line. Defaults to None.
    line_length : int, optional
        The length of the line before the comment starts. Defaults to 54.

    Returns
    -------

    """
    if comment is not None:
        if len(line) > line_length:
            comment = f" # {comment}\n"
        else:
            comment = f" {' ' * (line_length - len(line))}# {comment}\n"
        # Remove spaces before newline
        comment = comment.replace(" \n", "\n")
    else:
        comment = ""
    return line + comment
