from html import escape


def sanitize_input(input: str):
    return escape(' '.join(input.split()).lower())
