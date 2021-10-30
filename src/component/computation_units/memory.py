from src.component.computation_units.base_class import ComputationUnit
from src.component.intruction import Instruction, InstructionType
from src.component.registers.rat import RAT


class Memory(ComputationUnit):
    instruction_type = [InstructionType.LD, InstructionType.SD]

    # TODO: implement Queue
    def __init__(self, rat: RAT, latency: int, latency_mem: int, num_rs: int, num_units: int = 1):
        super().__init__(rat, latency, num_rs)
        self.latency_mem = latency_mem
        self.data = {}

    def decode_instruction(self, instruction: Instruction):
        instruction.operands[1] = int(instruction.operands[1])
        instruction.operands[2] = self.rat.get(instruction.operands[2])

        if instruction.type == InstructionType.LD:
            instruction.operands[0] = self.rat.reserve_rob(instruction.operands[0])
            instruction.destination = instruction.operands[0]
        if instruction.type == InstructionType.SD:
            instruction.operands[0] = self.rat.get(instruction.operands[0])
            instruction.destination = "NOP"

    def step_instruction(self, cycle, instruction):
        if self.resolve_operand(instruction, 2):
            memory_address = instruction.operands[1] + instruction.operands[2]
            if instruction.type == InstructionType.LD:
                instruction.result = self.data[memory_address] if memory_address in self.data else 0
            elif instruction.type == InstructionType.SD and self.resolve_operand(instruction, 0):
                self.data[memory_address] = instruction.operands[0]
                instruction.result = True
            else:
                return False

            instruction.stage_event.execute = (cycle, cycle + self.latency - 1)
            exe = instruction.stage_event.execute[1]
            if instruction.type == InstructionType.LD:
                instruction.stage_event.memory = (exe + 1, exe + self.latency_mem)
            if instruction.type == InstructionType.SD:
                instruction.stage_event.commit = (exe + 1, exe + self.latency_mem)
            return True

        return False
