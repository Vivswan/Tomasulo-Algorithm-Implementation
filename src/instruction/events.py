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
        r = [
            str(self.issue),
            str(self.execute if (self.execute is None or self.execute[0] != self.execute[1]) else self.execute[0]),
            str(self.memory if (self.memory is None or self.memory[0] != self.memory[1]) else self.memory[0]),
            str(self.write_back),
            str(self.commit if (self.commit is None or self.commit[0] != self.commit[1]) else self.commit[0]),
        ]
        return [("" if x == SKIP_TAG else x) for x in r]

    def __repr__(self):
        return f"{self.issue}, {self.execute}, {self.memory}, {self.write_back}, {self.commit}"
