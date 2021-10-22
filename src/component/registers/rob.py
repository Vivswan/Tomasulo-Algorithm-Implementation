from typing import Union

from src.component.registers.base_class import RegisterBase


class ROBField:
    type: str
    destination: str
    value: Union[int, float]
    finished: bool


class ROB(RegisterBase[ROBField]):
    prefix_tag = "ROB"

    def is_full(self):
        pass
