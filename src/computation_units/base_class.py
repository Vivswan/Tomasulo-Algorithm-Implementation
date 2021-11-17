from typing import Set, List, Union, Tuple

from src.instruction.instruction import InstructionType, Instruction
from src.registers.rat import RAT
from src.registers.rob import ROBField


class ComputationUnit:
    instruction_type: Union[Set[InstructionType], List[InstructionType]]
    require_rob: Union[Set[InstructionType], List[InstructionType]]

    def __init__(self, rat: RAT, latency: int, num_rs: int, pipelined=False):
        self.rat: RAT = rat
        self.latency: int = latency
        self.pipelined = pipelined
        self.buffer_limit: int = num_rs
        self.buffer_list: List[Instruction] = []
        self.execute_wait_for_result = True

    def is_empty(self) -> bool:
        return len(self.buffer_list) == 0

    def is_full(self) -> bool:
        return not (len(self.buffer_list) < self.buffer_limit)

    def decode_instruction(self, instruction: Instruction):
        raise NotImplemented

    def issue_instruction(self, instruction: Instruction):
        if self.is_full():
            raise Exception("Buffer list is full")
        if instruction.type not in self.instruction_type:
            raise Exception(f"Invalid Instruction type: {instruction.type}")

        self.buffer_list.append(instruction)

    @staticmethod
    def resolve_operand(instruction, operand_index):
        if not isinstance(instruction.operands[operand_index], ROBField):
            return True

        if instruction.operands[operand_index].finished:
            instruction.operands[operand_index] = instruction.operands[operand_index].value
            return True

        return False

    def step_execute(self, cycle: int):
        if not self.pipelined:
            for instruction in self.buffer_list:
                if instruction.stage_event.execute is None or instruction.stage_event.execute == "NOP":
                    continue
                if instruction.stage_event.execute[1] >= cycle:
                    return
                if self.has_result(cycle) and self.execute_wait_for_result:
                    return

        for instruction in self.buffer_list:
            if instruction.stage_event.issue >= cycle:
                continue

            if instruction.stage_event.execute is None:
                if self.step_execute_instruction(cycle, instruction):
                    return None

    def step_memory(self, cycle: int):
        pass

    def step_execute_instruction(self, cycle, instruction: Instruction) -> bool:
        raise NotImplemented

    def result_event(self, instruction: Instruction) -> Union[None, int]:
        raise NotImplemented

    def _result(self, cycle: int) -> Tuple[Union[int, float], Instruction]:
        ready_instructions = None
        minimum_cycle = float('inf')

        for i in self.buffer_list:
            ready_cycle = self.result_event(i)
            if ready_cycle is None or ready_cycle >= cycle:
                continue
            if minimum_cycle <= ready_cycle:
                continue
            if i.destination == "NOP":
                self.remove_instruction(i)
                continue
            minimum_cycle = ready_cycle
            ready_instructions = i

        return minimum_cycle, ready_instructions

    def has_result(self, cycle: int) -> bool:
        return self._result(cycle)[1] is not None

    def peak_result(self, cycle: int):
        if not self.has_result(cycle):
            raise Exception("No result found")

        return self._result(cycle)

    def remove_instruction(self, instruction: Union[Instruction, List[Instruction]]):
        if isinstance(instruction, list):
            for i in instruction:
                self.buffer_list.remove(i)
        else:
            self.buffer_list.remove(instruction)
