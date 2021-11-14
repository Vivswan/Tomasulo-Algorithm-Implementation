STRIKE_CHAR = "\u0336"


def strike(text: str):
    return STRIKE_CHAR + STRIKE_CHAR.join(text) + STRIKE_CHAR
