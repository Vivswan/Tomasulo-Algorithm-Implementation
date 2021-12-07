from typing import Tuple

from src.tags import SKIP_TAG


class StageEvent:
    rows = [
        "Issue",
        "Execute",
        "Memory",
        "Write Back",
        "Commit"
    ]

    def __init__(self):
        self.issue: int = None
        self.execute: Tuple[int, int] = None
        self.memory: Tuple[int, int] = None
        self.write_back: int = None
        self.commit: Tuple[int, int] = None

    def print_str(self):
        def _to_str(v):
            if isinstance(v, tuple):
                if v[0] == v[1]:
                    return str(v[0])
                else:
                    return f"{v[0]}-{v[1]}"

            if v == SKIP_TAG:
                return ""

            return str(v)

        return [_to_str(x) for x in [self.issue, self.execute, self.memory, self.write_back, self.commit]]

    def __repr__(self):
        return f"{self.issue}, {self.execute}, {self.memory}, {self.write_back}, {self.commit}"
