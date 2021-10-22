from typing import List, Callable

from src.component.intruction import Instruction


class CDB:
    num_of_lanes: int
    connected_to: List[Callable]

    def __init__(self, num_of_lanes: int):
        self.num_of_lanes = num_of_lanes

    def is_full(self):
        pass

    def send(self, instr: Instruction):
        pass
