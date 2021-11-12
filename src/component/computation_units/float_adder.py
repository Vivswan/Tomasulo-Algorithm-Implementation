from typing import Union

from src.component.computation_units.base_class import ComputationUnit
from src.component.instruction import Instruction, InstructionType


class FloatAdder(ComputationUnit):
    instruction_type = [InstructionType.ADDD, InstructionType.SUBD]
    require_rob = instruction_type

    def decode_instruction(self, instruction: Instruction):
        instruction.operands[1] = self.rat.get(instruction.operands[1])
        instruction.operands[2] = self.rat.get(instruction.operands[2])
        instruction.operands[0] = self.rat.reserve_rob(instruction.operands[0])
        instruction.destination = instruction.operands[0]
        instruction.stage_event.memory = "NOP"
        return instruction

    def step_execute_instruction(self, cycle, instruction: Instruction):
        if self.resolve_operand(instruction, 1) and self.resolve_operand(instruction, 2):
            if instruction.type == InstructionType.ADDD:
                instruction.result = instruction.operands[1] + instruction.operands[2]
            if instruction.type == InstructionType.SUBD:
                instruction.result = instruction.operands[1] - instruction.operands[2]

            instruction.stage_event.execute = (cycle, cycle + self.latency - 1)
            return True
        return False

    def result_event(self, instruction: Instruction) -> Union[None, int]:
        return instruction.stage_event.execute and instruction.stage_event.execute[1]
