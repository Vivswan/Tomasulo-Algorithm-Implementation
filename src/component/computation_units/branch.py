from src.component.computation_units.base_class import ComputationUnit
from src.component.intruction import Instruction, InstructionType


class Branch(ComputationUnit):
    instruction_type = [InstructionType.BEQ, InstructionType.BNE]

    def decode_instruction(self, instruction: Instruction):
        raise NotImplemented

    def step_instruction(self, cycle, instruction):
        raise NotImplemented
