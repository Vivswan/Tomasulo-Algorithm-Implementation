from src.component.computation_units.base_class import ComputationUnit
from src.component.events import processor_status
from src.component.intruction import Instruction, InstructionType


class FloatAdder(ComputationUnit):
    instruction_type = [InstructionType.ADDD, InstructionType.SUBD]
    latency = 3



    def step(self):
        for instruction in self.buffer_list:
            if instruction.result is None:
                compute = True
                for operand in instruction.operands:
                    if isinstance(operand, int) or isinstance(operand, float):
                        compute = False
                        break

                if compute:
                    if instruction.type == InstructionType.ADDD:
                        instruction.result = instruction.operands[1] + instruction.operands[2]

                    if instruction.type == InstructionType.SUBD:
                        instruction.result = instruction.operands[1] - instruction.operands[2]

                    instruction.stage_event.execute = (processor_status._cycle, processor_status._cycle + self.latency)

