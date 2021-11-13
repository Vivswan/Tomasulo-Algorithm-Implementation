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
        if key != 0:
            self.data[key] = value

    def print_table(self):
        for i, v in enumerate(self.data):
            i_str = f"{i}".zfill(int(math.log(len(self.data))) - 1)
            v_str = v if v == int(v) else f"{v:0.2f}"
            print(f"{i_str}: {v_str}".ljust(10), end="")

            if i % 16 == 0:
                print()

        print()


class IntegerRegister(RegisterBase[int]):
    pass


class FloatRegister(RegisterBase[float]):
    pass
