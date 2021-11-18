import os.path
import pathlib

from src.helper.strike import STRIKE_CHAR
from src.tomasulo import Tomasulo
from unit_tests import test_codes


def run_test_code(test_case: int):
    print()
    str_result = f"Running Test Case {test_case}...\n"
    code = test_codes[test_case]
    tomasulo = Tomasulo(code).run()

    str_result += "% Code %\n"
    str_result += code.strip()
    str_result += "\n\n"

    str_result += f"% Execution %\n"
    str_result += "\n"
    # print("\n".join([str(i) for i in tomasulo.instruction_buffer.history]) + "\n")
    str_result += tomasulo.instruction_buffer.print_str_history_table()
    str_result += "\n"

    str_result += f"% Registers %\n"
    str_result += tomasulo.rat.print_str_tables()
    str_result += tomasulo.memory_unit.print_str_tables()
    str_result += "\n"

    str_result += f"% Asserts %\n"
    assert_result, asserts = tomasulo.check_asserts()
    str_result += "\n".join([str(i) for i in asserts]) + "\n"
    str_result += f"asserts: {assert_result}"

    max_length = max(*[len(i.replace(STRIKE_CHAR, "").strip()) for i in str_result.split("\n")])
    str_result = "\n".join([(
                                i.replace("%", "-" * int((max_length - len(i)) / 2 + 2)) if "%" in i else i
                            ).rstrip() for i in str_result.split("\n")])

    max_length = max(*[len(i.strip().replace(STRIKE_CHAR, "")) for i in str_result.split("\n")])
    str_result = ("=" * max_length + "\n") + str_result + ("\n" + "=" * max_length)

    print(str_result)
    # print(tomasulo.unused_code_parameters)
    print()
    print()

    path = pathlib.Path(__file__).parent.resolve().joinpath(f"result")
    if not os.path.exists(path):
        os.mkdir(path)
    path = path.joinpath(f"result_{test_case}.txt")
    with open(path, "wb") as file:
        file.write(str_result.encode('utf-8'))


if __name__ == '__main__':
    for i in [1, 2, 3, 4]:
        run_test_code(i)
