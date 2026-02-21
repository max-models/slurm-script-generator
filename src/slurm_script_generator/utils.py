def add_line(line, comment=None, line_length=54):
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
