from src.component.computation_units.base_class import ComputationUnit
from src.component.intruction import Instruction, InstructionType


class FloatAdder(ComputationUnit):
    def issue_instruction(self, instruction: Instruction):
        super().issue_instruction(instruction)

        if not (instruction.type == InstructionType.ADDD or instruction.type == InstructionType.SUBD):
            raise Exception(f"Invalid Instruction type to float adder: {instruction.type}")


        # TODO

if __name__ == '__main__':
    instr = Instruction()