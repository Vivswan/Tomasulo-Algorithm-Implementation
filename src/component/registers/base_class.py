import re
from typing import List, Generic, TypeVar, Union

T = TypeVar('T')


class RegisterBase(Generic[T]):
    prefix_tag: str
    data: List[T]

    def __init__(self, num):
        if num < 0:
            raise ValueError(f"number of register cannot be less than 0: num = {num}")

        self.data = [0] * (num + 1)

    def get(self, index: Union[str, int]) -> T:
        if isinstance(index, int):
            return self[index]

        if isinstance(index, str):
            if re.fullmatch(self.prefix_tag + "[0-9]+", index) is not None:
                index = int(index[len(self.prefix_tag):])
                return self[index]

        raise Exception(f'Invalid Register Index "{str}", expected "{self.prefix_tag}[0-9]+"')

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
