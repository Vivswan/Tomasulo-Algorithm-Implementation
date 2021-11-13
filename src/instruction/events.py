from typing import Tuple


class StageEvent:
    def __init__(self):
        self.issue: int = None
        self.execute: Tuple[int, int] = None
        self.memory: Tuple[int, int] = None
        self.write_back: int = None
        self.commit: Tuple[int, int] = None

    def __repr__(self):
        return f"{self.issue}, {self.execute}, {self.memory}, {self.write_back}, {self.commit}"
