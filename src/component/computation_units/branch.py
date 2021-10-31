from src.component.computation_units.base_class import ComputationUnit
from src.component.intruction import Instruction, InstructionType


class Branch(ComputationUnit):
    instruction_type = [InstructionType.BEQ, InstructionType.BNE]

    def decode_instruction(self, instruction: Instruction):
        instruction.operands[0] = self.rat.get(instruction.operands[0])
        instruction.operands[1] = self.rat.get(instruction.operands[1])
        instruction.operands[2] = int(instruction.operands[2])
        instruction.destination = "NOP"
        return instruction

    def step_execute(self, cycle, instruction: Instruction):
        if self.resolve_operand(instruction, 0) and self.resolve_operand(instruction, 1):
            equality = instruction.operands[0] - instruction.operands[1]
            
            instruction.result = instruction.index + 1
            if instruction.type == InstructionType.BEQ and equality == 0:
                instruction.result += instruction.operands[2]
            if instruction.type == InstructionType.BNE and equality != 0:
                instruction.result += instruction.operands[2]

            instruction.stage_event.execute = (cycle, cycle + self.latency - 1)
            return True
        return False

    def is_busy(self):
        return len(self.buffer_list) > 0

    def mispredict(self, Predict_Index):
        pass
        # if calculated predicted Index is not the same as instruction.counter_index.
        # The Wipe all data from all feilds after misprediction.
