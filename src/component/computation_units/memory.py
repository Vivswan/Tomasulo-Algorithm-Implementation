import re
from typing import Union, Dict

from src.component.computation_units.base_class import ComputationUnit
from src.component.instruction import Instruction, InstructionType
from src.component.registers.rat import RAT


class Memory(ComputationUnit):
    instruction_type = [InstructionType.LD, InstructionType.SD]
    require_rob = [InstructionType.LD]

    # TODO: implement Queue
    def __init__(self, rat: RAT, latency: int, latency_mem: int, num_rs: int):
        super().__init__(rat, latency, num_rs)
        self.latency_mem = latency_mem
        self.data = {}
        self.execute_wait_for_result = False

    def decode_instruction(self, instruction: Instruction):
        instruction.operands[1] = int(instruction.operands[1])
        instruction.operands[2] = self.rat.get(instruction.operands[2])

        if instruction.type == InstructionType.LD:
            instruction.operands[0] = self.rat.reserve_rob(instruction.operands[0])
            instruction.destination = instruction.operands[0]
        if instruction.type == InstructionType.SD:
            instruction.operands[0] = self.rat.get(instruction.operands[0])
            instruction.destination = "NOP"
            instruction.stage_event.write_back = "NOP"
        return instruction

    def step_execute_instruction(self, cycle, instruction: Instruction) -> bool:
        if self.resolve_operand(instruction, 2):
            memory_address = instruction.operands[1] + instruction.operands[2]
            if memory_address % 4 != 0:
                raise Exception(f"Invalid memory address: {memory_address} % 4 != 0")

            if "memory_address" not in instruction.related_data:
                instruction.related_data["memory_address"] = memory_address
                instruction.stage_event.execute = (cycle, cycle + self.latency - 1)
                return True
        return False

    def step_memory_instruction(self, cycle, instruction: Instruction) -> bool:
        memory_address = instruction.related_data["memory_address"]
        for instr in self.buffer_list:
            if instruction.type == InstructionType.LD and instr.type == InstructionType.SD:
                if instr.counter_index < instruction.counter_index:
                    return False

        if instruction.type == InstructionType.LD:
            instruction.result = self.get_memory(memory_address)
        elif instruction.type == InstructionType.SD and self.resolve_operand(instruction, 0):
            self.set_memory(memory_address, instruction.operands[0])
            instruction.result = True
        else:
            return False

        memory_cycles = (cycle, cycle + self.latency_mem - 1)
        if instruction.type == InstructionType.LD:
            instruction.stage_event.memory = memory_cycles
        if instruction.type == InstructionType.SD:
            instruction.stage_event.memory = memory_cycles
            instruction.stage_event.commit = memory_cycles
        return True

    def set_values_from_parameters(self, parameters: Dict[str, str], remove_used=False):
        used_keys = []
        for key, value in parameters.items():
            if re.fullmatch("mem\[[0-9]+]", key.lower()) is None:
                continue
            address = int(key[4:-1])
            value = float(value)
            if address % 4 != 0:
                raise Exception(f"[compile time] Invalid memory address {address} % 4 != 0")
            self.set_memory(address, value)
            used_keys.append(key)

        if remove_used:
            for key in used_keys:
                del parameters[key]

    def get_memory(self, address):
        address = int(address)
        if address % 4 != 0:
            raise Exception(f"[run time] Invalid memory address {address} % 4 != 0")
        return self.data[address] if address in self.data else 0

    def set_memory(self, address, value):
        address = int(address)
        if address % 4 != 0:
            raise Exception(f"[run time] Invalid memory address {address} % 4 != 0")
        self.data[address] = value

    def result_event(self, instruction: Instruction) -> Union[None, int]:
        if instruction.type == InstructionType.LD:
            return instruction.stage_event.memory and instruction.stage_event.memory[1]
        if instruction.type == InstructionType.SD:
            return instruction.stage_event.commit and instruction.stage_event.commit[1]
