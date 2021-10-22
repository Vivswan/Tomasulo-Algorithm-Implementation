from typing import Optional, Set

from src.component.intruction import InstructionType, Instruction


class ComputationUnit:
    instruction_type: Set[InstructionType]

    def __init__(self, num_units, ):
        pass

    def is_full(self) -> bool:
        pass

    def issue_instruction(self, instruction: Instruction):
        instruction.stage_event.issue = 5
        pass

    def step(self):
        raise NotImplementedError

    def has_result(self) -> bool:
        pass

    def pop_result(self) -> Instruction:
        pass
