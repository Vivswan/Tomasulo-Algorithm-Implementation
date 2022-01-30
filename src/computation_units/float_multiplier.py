from src.computation_units.base_class import ComputationUnit
from src.instruction.instruction import Instruction, InstructionType
from src.tags import SKIP_TAG


class FloatMultiplier(ComputationUnit):
    instruction_type = [InstructionType.MULTD, InstructionType.DIVD]
    require_rob = instruction_type

    def decode_instruction(self, instruction: Instruction):
        instruction.operands[1] = self.rat.get(instruction.operands[1])
        instruction.operands[2] = self.rat.get(instruction.operands[2])
        instruction.operands[0] = self.rat.reserve_rob(instruction.operands[0])
        instruction.destination = instruction.operands[0]
        instruction.stage_event.memory = SKIP_TAG
        return instruction

    def step_execute_instruction(self, cycle, instruction: Instruction):
        if self.resolve_operand(instruction, 1) and self.resolve_operand(instruction, 2):
            if instruction.type == InstructionType.MULTD:
                instruction.result = instruction.operands[1] * instruction.operands[2]
            if instruction.type == InstructionType.DIVD:
                if instruction.operands[2] == 0:
                    raise NotImplementedError
                else:
                    instruction.result = instruction.operands[1] / instruction.operands[2]

            instruction.stage_event.execute = (cycle, cycle + self.latency - 1)
            return True
        return False
