from src.component.computation_units.base_class import ComputationUnit
from src.component.events import processor_status
from src.component.intruction import Instruction, InstructionType


class IntegerAdder(ComputationUnit):
    instruction_type = [InstructionType.ADDI, InstructionType.SUBI, InstructionType.ADD, InstructionType.SUB]
    latency = 1

    def decode_instruction(self, instruction: Instruction):
        instruction.operands[1] = self.rat.get(instruction.operands[1])

        if instruction.type in [InstructionType.ADDI, InstructionType.SUBI]:
            instruction.operands[2] = int(instruction.operands[2])

        if instruction.type in [InstructionType.ADD, InstructionType.SUB]:
            instruction.operands[2] = self.rat.get(instruction.operands[2])

        instruction.operands[0] = self.rat.reserve_rob(instruction.operands[0])
        instruction.destination = instruction.operands[0]
        return instruction

    def step_instruction(self, cycle, instruction):
        if self.resolve_operand(instruction, 1) and self.resolve_operand(instruction, 2):
            if instruction.type in [InstructionType.ADD, InstructionType.ADDI]:
                instruction.result = instruction.operands[1] + instruction.operands[2]
            if instruction.type in [InstructionType.SUB, InstructionType.SUBI]:
                instruction.result = instruction.operands[1] - instruction.operands[2]

            instruction.stage_event.execute = (cycle, cycle + self.latency - 1)
            return True
        else:
            return False
