from typing import Set, List, Union

from src.component.intruction import InstructionType, Instruction
from src.component.registers.rat import RAT
from src.component.registers.rob import ROBField


class ComputationUnit:
    instruction_type: Union[Set[InstructionType], List[InstructionType]]
    require_rob: Union[Set[InstructionType], List[InstructionType]]

    def __init__(self, rat: RAT, latency: int, num_rs: int):
        self.rat: RAT = rat
        self.latency: int = latency
        self.buffer_limit: int = num_rs
        self.buffer_list: List[Instruction] = []

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

    def step(self, cycle: int):
        for instruction in self.buffer_list:
            if instruction.stage_event.execute is None:
                continue
            if instruction.stage_event.execute[1] >= cycle:
                return
            if instruction.stage_event.write_back is None:
                return

        for instruction in self.buffer_list:
            if instruction.stage_event.issue >= cycle:
                continue

            if instruction.result is None:
                if self.step_execute(cycle, instruction):
                    return None

    @staticmethod
    def resolve_operand(instruction, operand_index):
        if not isinstance(instruction.operands[operand_index], ROBField):
            return True

        if instruction.operands[operand_index].finished:
            instruction.operands[operand_index] = instruction.operands[operand_index].value
            return True

        return False

    def step_execute(self, cycle, instruction: Instruction) -> bool:
        raise NotImplemented

    def _result(self, cycle: int) -> List[Instruction]:
        ready_instructions = []
        for i in self.buffer_list:
            max_cycle = -1

            if -1 in [i.stage_event.execute, i.stage_event.memory, i.stage_event.commit]:
                continue

            if i.stage_event.execute is not None:
                max_cycle = max(max_cycle, i.stage_event.execute[1])

            if i.stage_event.memory is not None:
                max_cycle = max(max_cycle, i.stage_event.memory[1])

            if i.stage_event.commit is not None:
                max_cycle = max(max_cycle, i.stage_event.commit[1])

            if max_cycle == -1:
                continue

            if max_cycle < cycle:
                ready_instructions.append(i)

        return ready_instructions

    def has_result(self, cycle: int) -> bool:
        return len(self._result(cycle)) > 0

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
