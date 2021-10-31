from src.tomasulo import Tomasulo
from unit_tests import test_codes

if __name__ == '__main__':
    code = test_codes[1]
    tomasulo = Tomasulo(code)

    while tomasulo._cycle < 100:
        tomasulo.step()

    for k in tomasulo.instruction_buffer.history:
        print(k)
