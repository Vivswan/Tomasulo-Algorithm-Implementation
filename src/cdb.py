from typing import List

from src.computation_units.base_class import ComputationUnit
from src.instruction.instruction import Instruction
from src.instruction.instruction_buffer import InstructionBuffer
from src.registers.rat import RAT
from src.tags import NULL_TAG, SKIP_TAG


class CDB:
    def __init__(
            self,
            num_cdb: int,
            cdb_buffer_size: int,
            computational_units: List[ComputationUnit],
            instruction_buffer: InstructionBuffer,
            rat: RAT
    ):
        self.num_cdb = num_cdb
        self.cdb_buffer_size = cdb_buffer_size
        self.cdb_buffer = []
        self.computational_units = computational_units
        self.instruction_buffer = instruction_buffer
        self.rat = rat

    def pull_results(self, cycle: int):
        results: List[Instruction] = []
        for unit in self.computational_units:
            if unit.has_result(cycle=cycle):
                results += unit.peak_result(cycle=cycle)

        results.sort(key=lambda x: (x.related_data["computation_ready"], x.counter_index))
        results = self.cdb_buffer + results

        return results

    def write_back(self, destination, result) -> bool:
        if destination == NULL_TAG:
            return True
        if destination == SKIP_TAG:
            return False

        rob_entry = self.rat.set_rob_value(destination, result)
        for instr in self.instruction_buffer.history:
            if rob_entry not in instr.operands:
                continue
            instr.operands[instr.operands.index(rob_entry)] = rob_entry.value
        return True

    def send_results(self, cycle: int, results: List[Instruction]):
        remaining = results.copy()
        count_write_back = 0

        for instruction in results:
            if count_write_back >= self.num_cdb:
                break
            if instruction.related_data["computation_ready"] >= cycle:
                continue

            if instruction in self.cdb_buffer:
                self.cdb_buffer.remove(instruction)
            else:
                instruction.computation_unit.remove_instruction(instruction)

            if self.write_back(instruction.destination, instruction.result):
                count_write_back += 1

            remaining.remove(instruction)
            instruction.stage_event.write_back = cycle

        return remaining

    def save_to_buffer(self, results):
        for instruction in results:
            if len(self.cdb_buffer) >= self.cdb_buffer_size:
                break
            if instruction in self.cdb_buffer:
                continue
            instruction.computation_unit.remove_instruction(instruction)
            self.cdb_buffer.append(instruction)

    def step(self, cycle: int):
        results = self.pull_results(cycle)
        results = self.send_results(cycle, results)
        self.save_to_buffer(results)
