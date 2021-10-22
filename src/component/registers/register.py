from typing import Union

from src.component.registers.base_class import RegisterBase


class Register(RegisterBase[Union[int, float]]):
    prefix_tag = "ARF"
    pass
