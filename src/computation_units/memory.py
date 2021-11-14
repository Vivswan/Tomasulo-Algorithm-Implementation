import math
import re
from typing import Union, Dict, List

from src.computation_units.base_class import ComputationUnit
from src.instruction.instruction import Instruction, InstructionType
from src.registers.rat import RAT


class Memory(ComputationUnit):
    instruction_type = [InstructionType.LD, InstructionType.SD]
    require_rob = [InstructionType.LD]

    def __init__(
            self,
            rat: RAT,
            latency: int,
            ram_size: int,
            ram_latency: int,
            queue_latency: int,
            queue_size: int
    ):
        super().__init__(rat, latency, queue_size)
        self.ram_size = ram_size
        self.queue_size = queue_size
        self.ram_latency = ram_latency
        self.cache_latency = queue_latency
        self.execute_wait_for_result = False

        self.data = [0] * ram_size
        self.to_set_data = []

        self.load_store_queue = []

    def issue_instruction(self, instruction: Instruction):
        super().issue_instruction(instruction)
        self.load_store_queue.append(instruction)
        while len(self.load_store_queue) > self.queue_size:
            self.load_store_queue.pop(0)

    def remove_instruction(self, instruction: Union[Instruction, List[Instruction]]):
        super().remove_instruction(instruction)
        if not instruction.execution and instruction in self.load_store_queue:
            self.load_store_queue.remove(instruction)

    def set_values_from_parameters(self, parameters: Dict[str, str], remove_used=False):
        used_keys = []
        for key, value in parameters.items():
            if re.fullmatch("mem\[[0-9]+\]", key.lower()) is None:
                continue
            address = int(key[4:-1])
            value = float(value)
            value = int(value) if value == int(value) else value
            if address % 4 != 0:
                raise Exception(f"[compile time] Invalid memory address {address} % 4 != 0")
            self.set_value(address, value)
            used_keys.append(key)

        if remove_used:
            for key in used_keys:
                del parameters[key]

    def get_value(self, address):
        address = int(address)
        if address % 4 != 0:
            raise Exception(f"[run time] Invalid memory address {address} % 4 != 0")
        address = int(address / 4)
        return self.data[address]

    def set_value(self, address, value):
        address = int(address)
        if address % 4 != 0:
            raise Exception(f"[run time] Invalid memory address {address} % 4 != 0")
        address = int(address / 4)
        self.data[address] = value

    def decode_instruction(self, instruction: Instruction):
        instruction.operands[1] = int(instruction.operands[1])
        instruction.operands[2] = self.rat.get(instruction.operands[2])
        instruction.related_data['memory_address'] = None

        if instruction.type == InstructionType.LD:
            instruction.operands[0] = self.rat.reserve_rob(instruction.operands[0])
            instruction.destination = instruction.operands[0]
        if instruction.type == InstructionType.SD:
            instruction.operands[0] = self.rat.get(instruction.operands[0])
            instruction.result = "NOP"
            instruction.destination = "NOP"
            instruction.stage_event.write_back = "NOP"
        return instruction

    def step_execute_instruction(self, cycle, instruction: Instruction) -> bool:
        if self.resolve_operand(instruction, 2):
            memory_address = instruction.operands[1] + instruction.operands[2]
            if memory_address % 4 != 0:
                raise Exception(f"Invalid memory address: {memory_address} % 4 != 0")

            if instruction.related_data["memory_address"] is None:
                instruction.related_data["memory_address"] = memory_address
                instruction.stage_event.execute = (cycle, cycle + self.latency - 1)
                return True
        return False

    def step_memory(self, cycle: int):
        to_compute: Instruction = None

        for check in self.buffer_list:
            if check.related_data["memory_address"] is None:
                return None
            if check.stage_event.memory is None:
                to_compute = check
                break
            if check.stage_event.memory[1] >= cycle:
                return None

        if to_compute is None:
            return None

        latency = self.ram_latency
        if to_compute.type == InstructionType.LD:
            for check in reversed(self.load_store_queue[:self.load_store_queue.index(to_compute)]):
                if check.related_data["memory_address"] == to_compute.related_data["memory_address"]:
                    if check.type == InstructionType.LD:
                        to_compute.result = check.result
                    if check.type == InstructionType.SD:
                        to_compute.result = check.operands[0]
                    latency = self.cache_latency
                    break
            if to_compute.result is None:
                to_compute.result = self.get_value(to_compute.related_data["memory_address"])
            to_compute.stage_event.memory = (cycle, cycle + latency - 1)

        if to_compute.type == InstructionType.SD:
            if to_compute.prev is not None:
                if to_compute.prev.stage_event.commit is None:
                    return None
                if to_compute.prev.stage_event.commit[1] >= cycle:
                    return None

            self.set_value(to_compute.related_data["memory_address"], to_compute.operands[0])
            to_compute.stage_event.memory = (cycle, cycle + latency - 1)
            to_compute.stage_event.commit = to_compute.stage_event.memory

    def result_event(self, instruction: Instruction) -> Union[None, int]:
        if instruction.type == InstructionType.LD:
            return instruction.stage_event.memory and instruction.stage_event.memory[1]
        if instruction.type == InstructionType.SD:
            return instruction.stage_event.commit and instruction.stage_event.commit[1]

    def print_str_tables(self):
        str_result = ""
        str_result += "Memory - \n"
        count = 1
        for i, v in enumerate(self.data):
            if v != 0:
                i_str = f"{i * 4}".zfill(math.ceil(math.log10(len(self.data) * 4)))
                v_str = v if v == int(v) else f"{v:0.2f}"
                str_result += f"{i_str}: {v_str}".ljust(10)
                count += 1

            if count % 16 == 0:
                str_result += "\n"

        str_result += "\n"
        return str_result
