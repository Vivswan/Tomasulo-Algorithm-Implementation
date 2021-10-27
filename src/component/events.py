from typing import Tuple


class StageEvent:
    issue: int = None
    execute: Tuple[int, int] = None
    memory: Tuple[int, int] = None
    write_back: int = None
    commit: int = None

    def __repr__(self):
        return f"{self.issue}, {self.execute}, {self.memory}, {self.write_back}, {self.commit}"


class Processor:
    cycle: int = -1


processor_status = Processor()
