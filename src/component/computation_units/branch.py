from src.component.computation_units.base_class import ComputationUnit
from src.component.intruction import Instruction, InstructionType

# The amount of predictions allowed to be kept.
# Predictions will be based on Index numbers, not counter numbers.
# 8 entries correspond to the last three digits of the PC (In our case the Index)
from src.component.registers.rat import RAT
from src.helper.extract_bits import extract_rbits


class Branch(ComputationUnit):
    instruction_type = [InstructionType.BEQ, InstructionType.BNE]

    def __init__(self, rat: RAT, latency: int, num_rs: int):
        super().__init__(rat, latency, num_rs)
        self.btb_limit = 3
        self.btb_table = [False] * (2 ** self.btb_limit)

    def decode_instruction(self, instruction: Instruction):
        instruction.operands[0] = self.rat.get(instruction.operands[0])
        instruction.operands[1] = self.rat.get(instruction.operands[1])
        instruction.operands[2] = int(instruction.operands[2])
        instruction.destination = "NOP"
        instruction.stage_event.write_back = "NOP"
        return instruction

    def step_execute(self, cycle, instruction: Instruction):
        if self.resolve_operand(instruction, 0) and self.resolve_operand(instruction, 1):
            equality = instruction.operands[0] - instruction.operands[1]
            self.check_prediction(instruction, equality)
            instruction.result = 0
            instruction.result = instruction.index + 1

            if instruction.type == InstructionType.BEQ and equality == 0:
                instruction.result += instruction.operands[2]
            if instruction.type == InstructionType.BNE and equality != 0:
                instruction.result += instruction.operands[2]

            instruction.stage_event.execute = (cycle, cycle + self.latency - 1)
            return True
        return False

    def is_busy(self):
        return len(self.buffer_list) > self.buffer_limit

    # Updates in the execute stage and checks for misprediction
    def check_prediction(self, instruction: Instruction, equality):
        instruction.branch_prediction_accurate = True

        if instruction.type is InstructionType.BEQ and instruction.branch_jump == (equality == 0):
            return None

        if instruction.type is InstructionType.BNE and instruction.branch_jump == (equality != 0):
            return None

        instruction.branch_prediction_accurate = False
        instruction.related_data['branch_correction'] = True

        num_int = extract_rbits(instruction.index, self.btb_limit)
        self.btb_table[num_int] = not self.btb_table[num_int]

    # This has to run in the Issue state and gives the next instruction.
    def branch_prediction(self, instruction: Instruction):
        if instruction.type not in [InstructionType.BEQ, InstructionType.BNE]:
            raise Exception("instruction type is not a branch")

        num_int = extract_rbits(instruction.index, self.btb_limit)
        instruction.branch_jump = self.btb_table[num_int]

        if instruction.branch_jump:
            return int(instruction.operands[2])
        else:
            return 0
