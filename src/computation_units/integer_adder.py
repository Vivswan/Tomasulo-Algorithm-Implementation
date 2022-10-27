from src.computation_units.base_class import ComputationUnit
from src.computation_units.branch_prediction import Branch
from src.instruction.instruction import Instruction, InstructionType
from src.registers.rat import RAT
from src.tags import SKIP_TAG


class IntegerAdder(ComputationUnit):
    integer_instruction_type = [InstructionType.ADDI, InstructionType.SUBI, InstructionType.ADD, InstructionType.SUB]
    integer_require_rob = integer_instruction_type

    def __init__(self, rat: RAT, latency: int, num_rs: int, btb_limit=3, pipelined=False):
        super().__init__(rat, latency, num_rs, pipelined)
        self.branch_unit = Branch(parent=self, btb_limit=btb_limit)
        self.instruction_type = self.integer_instruction_type + self.branch_unit.instruction_type
        self.require_rob = self.integer_require_rob + self.branch_unit.require_rob

    def decode_instruction(self, instruction: Instruction):
        if instruction.type in self.integer_instruction_type:
            return self.decode_integer_instruction(instruction)
        if instruction.type in self.branch_unit.instruction_type:
            return self.branch_unit.decode_instruction(instruction)

    def step_execute_instruction(self, cycle, instruction: Instruction):
        if instruction.type in self.integer_instruction_type:
            return self.step_integer_execute(cycle, instruction)
        if instruction.type in self.branch_unit.instruction_type:
            return self.branch_unit.step_execute(cycle, instruction)
        return False

    def decode_integer_instruction(self, instruction: Instruction):
        instruction.operands[1] = self.rat.get(instruction.operands[1])

        if instruction.type in [InstructionType.ADDI, InstructionType.SUBI]:
            instruction.operands[2] = int(instruction.operands[2])

        if instruction.type in [InstructionType.ADD, InstructionType.SUB]:
            instruction.operands[2] = self.rat.get(instruction.operands[2])

        instruction.operands[0] = self.rat.reserve_rob(instruction.operands[0])
        instruction.destination = instruction.operands[0]
        instruction.stage_event.memory = SKIP_TAG
        return instruction

    def step_integer_execute(self, cycle, instruction: Instruction):
        if self.resolve_operand(instruction, 1) and self.resolve_operand(instruction, 2):
            if instruction.type in [InstructionType.ADD, InstructionType.ADDI]:
                instruction.result = instruction.operands[1] + instruction.operands[2]
            if instruction.type in [InstructionType.SUB, InstructionType.SUBI]:
                instruction.result = instruction.operands[1] - instruction.operands[2]

            instruction.stage_event.execute = (cycle, cycle + self.latency - 1)
            return True
        return False
