from dataclasses import dataclass
from typing import Union


@dataclass
class AssertResult:
    result: bool
    key: str
    check_value: Union[str, int, float, bool]
    value: Union[str, int, float, bool]

    def __repr__(self) -> str:
        return f"{self.key} ({self.result}): {self.check_value} {'==' if self.result else '!='} {self.value}"
