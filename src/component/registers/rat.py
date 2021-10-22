from typing import Union

from src.component.registers.base_class import RegisterBase


class RAT(RegisterBase[Union[str]]):
    prefix_tag = "R"
    pass
