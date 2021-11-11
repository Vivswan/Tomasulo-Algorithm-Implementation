import math
from dataclasses import dataclass
from typing import Union

from src.component.registers.registers import RegisterBase


@dataclass
class ROBField:
    destination: str
    value: Union[int, float] = None
    finished: bool = False
    index: str = ""


class ROB(RegisterBase[ROBField]):
    def __init__(self, num):
        super().__init__(num, None)
        self.pointer = 1

    def _get_free_rob_index_circular(self):
        if not any([i is None for i in self.data[1:]]):
            return None

        while True:
            self.pointer %= len(self.data)
            if self.pointer == 0:
                self.pointer += 1

            if self.data[self.pointer] is None:
                return self.pointer

            self.pointer += 1

    def _get_free_rob_index_linear(self):
        for i, v in enumerate(self.data):
            if v is None and i != 0:
                return i
        return None

    def _get_free_rob_index(self):
        return self._get_free_rob_index_circular()

    def is_full(self):
        return self._get_free_rob_index() is None

    def reserve_for(self, register_index: str):
        free_rob_index = self._get_free_rob_index()
        self.pointer += 1
        if free_rob_index is None:
            raise Exception("No free ROB")

        new_value = ROBField(destination=register_index, index=f"ROB{free_rob_index}")
        self.data[free_rob_index] = new_value
        return f"ROB{free_rob_index}", new_value

    def is_value_available(self, index: int):
        return self.data[index].finished

    def print_table(self):
        just = 20
        count = 1
        for i, v in enumerate(self.data):
            i_str = f"{i}".zfill(int(math.log(len(self.data))) - 1)
            if v is not None:
                if not v.finished:
                    print(f"{i_str}: {v.destination}".ljust(just), end="")
                else:
                    value = v.value if v.value == int(v.value) else f"{v.value:0.2f}"
                    print(f"{i_str}: {v.destination} - {value}".ljust(just), end="")
                count += 1
            # else:
            #     print(f"{i_str}".ljust(just), end="")

            if count % 8 == 0:
                print()

        print()

    def set_value(self, index, value):
        self.data[index].value = value
        self.data[index].finished = True
        return self.data[index]

    def remove(self, index: int):
        self.data[index] = None
