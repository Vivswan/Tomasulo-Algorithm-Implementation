def strike(text):
    result = ''
    for c in text:
        result = result + c + '\u0336'
    return result
