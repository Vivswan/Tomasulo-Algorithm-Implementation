from src.tomasulo import Tomasulo
from unit_tests import test_codes

if __name__ == '__main__':
    code = test_codes[0]
    tomasulo = Tomasulo(code).run()

    for k in tomasulo.instruction_buffer.history:
        print(k)
    print()
    assert_result, asserts = tomasulo.check_asserts()
    for a in asserts:
        print(a)
    print(f"asserts: {assert_result}")
