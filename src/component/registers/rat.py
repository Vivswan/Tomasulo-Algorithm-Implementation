import re
from typing import Tuple

from src.component.registers.registers import IntegerRegister, FloatRegister, RegisterBase
from src.component.registers.rob import ROB, ROBField


class RAT:
    def __init__(self, num_integer_register: int, num_float_register: int, num_rob: int):
        self.num_integer_register = num_integer_register
        self.num_float_register = num_float_register
        self.num_rob = num_rob

        self.integer_register = IntegerRegister(num_integer_register)
        self.float_register = FloatRegister(num_float_register)
        self.rob = ROB(num_rob)

        self.all_tables = [self.integer_register, self.float_register, self.rob]
        self.reference_dict = {}

    def get(self, index, raise_error=True):
        obj, obj_index = self._get_index(index, raise_error=raise_error)

        if (not raise_error) and obj is None:
            return None

        value = obj[obj_index]
        if isinstance(value, ROBField) and value.finished:
            return value.value

        return value

    def is_value_available(self, index):
        obj, obj_index = self._get_index(index)

        if obj == self.rob:
            return self.rob.is_value_available(obj_index)
        else:
            return True

    def reserve_rob(self, register_index):
        if self.rob.is_full():
            raise Exception("ROB is full")
        self._get_index(register_index)

        rob_index, rob_value = self.rob.reserve_for(register_index)
        self.reference_dict[register_index] = rob_index
        return rob_index

    def set_rob_value(self, rob_index, value):
        rob, rob_i = self._get_index(rob_index)
        if rob != self.rob:
            raise Exception(f"Invalid index: {rob_index}")

        return self.rob.set_value(rob_i, value)

    def commit_rob(self, rob_index):
        rob, rob_i = self._get_index(rob_index)
        if rob != self.rob:
            raise Exception(f"Invalid index: {rob_index}")

        rob_value = self.rob[rob_i]
        if rob_index == self.reference_dict[rob_value.destination]:
            self.reference_dict[rob_value.destination] = rob_value.destination

        register, register_index = self._get_index(rob_value.destination, use_references=False)
        register[register_index] = rob_value.value

        self.rob.remove(rob_i)

    def remove_rob(self, rob_index):
        rob, rob_i = self._get_index(rob_index)
        if rob != self.rob:
            raise Exception(f"Invalid index: {rob_index}")

        rob_value = self.rob[rob_i]
        if rob_index == self.reference_dict[rob_value.destination]:
            self.reference_dict[rob_value.destination] = rob_value.destination

        self.rob.remove(rob_i)

    def _get_index(self, index: str, use_references=True, raise_error=True) -> Tuple[RegisterBase, int]:
        if index in self.reference_dict and index != self.reference_dict[index] and use_references:
            return self._get_index(self.reference_dict[index])

        if re.fullmatch("R[0-9]+", index) is not None:
            return self.integer_register, int(index.replace("R", ""))
        if re.fullmatch("F[0-9]+", index) is not None:
            return self.float_register, int(index.replace("F", ""))
        if re.fullmatch("ROB[0-9]+", index) is not None:
            return self.rob, int(index.replace("ROB", ""))

        if raise_error:
            raise Exception(f"Invalid Index: {index}")
        else:
            return None, None

    def print_tables(self):
        print("Integer Register -  ", end="")
        self.integer_register.print_table()
        print("Float Register -    ", end="")
        self.float_register.print_table()
        print("ROB -               ", end="")
        self.rob.print_table()

    def set_values_from_parameters(self, parameters: dict, remove_used=False):
        used_keys = []
        for key, value in parameters.items():
            reg, reg_i = self._get_index(key, use_references=False, raise_error=False)
            try:
                if reg is self.integer_register:
                    reg[reg_i] = int(value)
                    used_keys.append(key)
                if reg is self.float_register:
                    reg[reg_i] = float(value)
                    used_keys.append(key)
            except:
                raise ValueError(f'[compile time] Invalid type of value for "{key}": found "{value}"')

        if remove_used:
            for key in used_keys:
                del parameters[key]

if __name__ == '__main__':
    rat = RAT(3, 3, 3)
    rat.integer_register.set_full_data([3, 2, 1])
    rat.float_register.set_full_data([3.3, 2.2, 1.1])
    # rat.integer_register.print_table()
    # rat.float_register.print_table()

    print(f"R1: {rat.get('R1')}")
    print(f"R0: {rat.get('R0')}")
    print(f"F2: {rat.get('F2')}")
    rob_index = rat.reserve_rob("F2")
    print(f"F2: {rat.get('F2')}")
    rat.set_rob_value(rob_index, 2)
    print(f"F2: {rat.get('F2')}")
    rat.commit_rob(rob_index)
    print(f"F2: {rat.get('F2')}")
    print()
    rat.print_tables()
