import math
from typing import List, Generic, TypeVar

T = TypeVar('T')


class RegisterBase(Generic[T]):
    def __init__(self, num, default_value=0):
        if num < 0:
            raise ValueError(f"number of register cannot be less than 0: num = {num}")

        self.data: List[T] = [default_value] * (num + 1)

    def get(self, index: int) -> T:
        return self[index]

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value: T):
        if key >= len(self.data):
            raise Exception("register out of range")
        if key != 0:
            self.data[key] = value

    def print_str_tables(self):
        str_result = ""
        for i, v in enumerate(self.data):
            i_str = f"{i}".zfill(math.ceil(math.log10(len(self.data))))
            v_str = v if v == int(v) else f"{v:0.2f}"
            str_result += f"{i_str}: {v_str}".ljust(10)

            if i % 16 == 0:
                str_result += "\n"

        str_result += "\n"
        return str_result


class IntegerRegister(RegisterBase[int]):
    def __setitem__(self, key, value: T):
        super().__setitem__(key, int(value))


class FloatRegister(RegisterBase[float]):
    def __setitem__(self, key, value: T):
        super().__setitem__(key, float(value))
