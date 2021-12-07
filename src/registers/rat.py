import copy
import re
from typing import Tuple

from src.registers.registers import IntegerRegister, FloatRegister, RegisterBase
from src.registers.rob import ROB, ROBField


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
        self.reference_dict_copies = {}

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

    def commit_rob(self, rob_index, write_back=True):
        rob, rob_i = self._get_index(rob_index)
        if rob != self.rob:
            raise Exception(f"Invalid index: {rob_index}")

        rob_value = self.rob[rob_i]
        if rob_index == self.reference_dict[rob_value.destination]:
            self.reference_dict[rob_value.destination] = rob_value.destination
            for key, value in self.reference_dict_copies.items():
                if rob_index == value[rob_value.destination]:
                    value[rob_value.destination] = rob_value.destination

        if write_back:
            register, register_index = self._get_index(rob_value.destination, use_references=False)
            register[register_index] = rob_value.value

        self.rob.remove(rob_i)

    def make_copy_on_id(self, copy_id):
        self.reference_dict_copies[copy_id] = copy.deepcopy(self.reference_dict)

    def reverse_rat_to_copy(self, copy_id):
        self.reference_dict = copy.deepcopy(self.reference_dict_copies[copy_id])
        for key in list(self.reference_dict_copies.keys()):
            if key > copy_id:
                self.remove_rat_copy(key)

    def remove_rat_copy(self, copy_id):
        del self.reference_dict_copies[copy_id]

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

    def print_str_tables(self, print_rob=False):
        str_result = ""
        str_result += "Integer Register -  "
        str_result += self.integer_register.print_str_tables()
        str_result += "Float Register -    "
        str_result += self.float_register.print_str_tables()
        if print_rob:
            str_result += "ROB -               "
            str_result += self.rob.print_str_tables()
        return str_result

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
