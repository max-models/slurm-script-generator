def add_line(line, comment="", line_length=40):
    if len(comment) > 0:
        if len(line) > line_length:
            comment = f" # {comment}\n"
        else:
            comment = f" {' ' * (line_length - len(line))}# {comment}\n"
    return line + comment
