STRIKE_CHAR = "\u0336"


def strike(text: str):
    result = ''
    for c in text:
        result = result + c + STRIKE_CHAR
    return result
