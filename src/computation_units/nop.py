from src.computation_units.base_class import ComputationUnit
from src.instruction.instruction import Instruction, InstructionType
from src.registers.rat import RAT
from src.tags import SKIP_TAG, NULL_TAG


class NOPUnit(ComputationUnit):
    instruction_type = [InstructionType.NOP]
    require_rob = []

    def decode_instruction(self, instruction: Instruction):
        instruction.result = NULL_TAG
        instruction.destination = NULL_TAG
        instruction.stage_event.memory = SKIP_TAG
        return instruction

    def step_execute_instruction(self, cycle, instruction: Instruction):
        instruction.stage_event.execute = (cycle, cycle + self.latency - 1)
        return True

    def is_full(self) -> bool:
        return False
