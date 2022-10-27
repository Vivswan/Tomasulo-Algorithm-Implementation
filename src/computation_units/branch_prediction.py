from src.computation_units.base_class import ComputationUnit
from src.helper.extract_bits import extract_rbits
from src.instruction.instruction import Instruction, InstructionType
from src.tags import SKIP_TAG


class Branch:
    instruction_type = [InstructionType.BEQ, InstructionType.BNE]
    require_rob = []

    def __init__(self, parent: ComputationUnit, btb_limit: int):
        self.parent = parent
        self.btb_limit = btb_limit
        self.btb_table = [False] * (2 ** self.btb_limit)

    def decode_instruction(self, instruction: Instruction):
        instruction.operands[0] = self.parent.rat.get(instruction.operands[0])
        instruction.operands[1] = self.parent.rat.get(instruction.operands[1])
        instruction.operands[2] = int(instruction.operands[2])
        instruction.related_data['branch_prediction_accurate'] = None
        instruction.destination = SKIP_TAG
        instruction.stage_event.memory = SKIP_TAG
        instruction.stage_event.write_back = SKIP_TAG
        return instruction

    def step_execute(self, cycle, instruction: Instruction):
        if self.parent.resolve_operand(instruction, 0) and self.parent.resolve_operand(instruction, 1):
            equality = instruction.operands[0] - instruction.operands[1]
            self.check_prediction(instruction, equality)
            instruction.result = 0
            instruction.result = instruction.index + 1

            if instruction.type == InstructionType.BEQ and equality == 0:
                instruction.result += instruction.operands[2]
            if instruction.type == InstructionType.BNE and equality != 0:
                instruction.result += instruction.operands[2]

            instruction.stage_event.execute = (cycle, cycle + self.parent.latency - 1)
            return True
        return False

    def is_busy(self):
        return len(self.parent.buffer_list) > self.parent.buffer_limit

    # Updates in to execute stage and checks for misprediction
    def check_prediction(self, instruction: Instruction, equality):
        instruction.related_data['branch_prediction_accurate'] = True

        if instruction.type is InstructionType.BEQ and instruction.related_data["branch_jump"] == (equality == 0):
            return None

        if instruction.type is InstructionType.BNE and instruction.related_data["branch_jump"] == (equality != 0):
            return None

        instruction.related_data['branch_prediction_accurate'] = False
        instruction.related_data['branch_correction'] = True

        num_int = extract_rbits(instruction.index, self.btb_limit)
        self.btb_table[num_int] = not self.btb_table[num_int]

    # This has to run in the Issue state and gives the next instruction.
    def predict(self, instruction: Instruction):
        if instruction.type not in [InstructionType.BEQ, InstructionType.BNE]:
            raise Exception("instruction type is not a branch")

        num_int = extract_rbits(instruction.index, self.btb_limit)
        instruction.related_data["branch_jump"] = self.btb_table[num_int]

        if instruction.related_data["branch_jump"]:
            return int(instruction.operands[2])
        return 0
