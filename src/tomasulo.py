import ast
import copy
from typing import List, Tuple

from src.computation_units.base_class import ComputationUnit
from src.computation_units.float_adder import FloatAdder
from src.computation_units.float_multiplier import FloatMultiplier
from src.computation_units.integer_adder import IntegerAdder
from src.computation_units.memory import Memory
from src.default_parameters import TOMASULO_DEFAULT_PARAMETERS
from src.instruction.assert_result import AssertResult
from src.instruction.instruction_buffer import InstructionBuffer
from src.registers.rat import RAT


class Tomasulo:
    _cycle = 1

    def __init__(self, full_code):
        self.parameters = copy.deepcopy(TOMASULO_DEFAULT_PARAMETERS)

        self.instruction_buffer = InstructionBuffer()
        self.instruction_buffer.append_code(full_code)
        self.unused_code_parameters = copy.deepcopy(self.instruction_buffer.code_parameters)
        self.set_parameters(self.unused_code_parameters, remove_used=True)

        self.rat = RAT(
            num_integer_register=self.parameters["num_register"],
            num_float_register=self.parameters["num_register"],
            num_rob=self.parameters["num_rob"]
        )
        self.rat.set_values_from_parameters(self.unused_code_parameters, remove_used=True)

        self.integer_adder = IntegerAdder(
            rat=self.rat,
            latency=self.parameters["integer_adder_latency"],
            num_rs=self.parameters["integer_adder_rs"]
        )
        self.float_adder = FloatAdder(
            rat=self.rat,
            latency=self.parameters["float_adder_latency"],
            num_rs=self.parameters["float_adder_rs"]
        )
        self.float_multiplier = FloatMultiplier(
            rat=self.rat,
            latency=self.parameters["float_multiplier_latency"],
            num_rs=self.parameters["float_multiplier_rs"]
        )
        self.memory_unit = Memory(
            rat=self.rat,
            latency=self.parameters["memory_unit_latency"],
            ram_latency=self.parameters["memory_unit_ram_latency"],
            queue_latency=self.parameters["memory_unit_queue_latency"],
            ram_size=self.parameters["memory_unit_ram_size"],
            queue_size=self.parameters["memory_unit_queue_size"]
        )
        self.memory_unit.set_values_from_parameters(self.unused_code_parameters, remove_used=True)
        self.computational_units: List[ComputationUnit] = [
            self.integer_adder,
            self.float_adder,
            self.float_multiplier,
            self.memory_unit,
        ]

    def set_parameters(self, parameters: dict, remove_used=False):
        used_keys = []
        for key, value in parameters.items():
            if key in self.parameters:
                parsed_value = ast.literal_eval(value)
                if not isinstance(parsed_value, type(self.parameters[key])):
                    raise ValueError(
                        f'Invalid type for "{key}"'
                        f', expected: {type(self.parameters[key])}'
                        f', got: {type(parsed_value)}'
                    )
                self.parameters[key] = parsed_value
                used_keys.append(key)

        if remove_used:
            for key in used_keys:
                del parameters[key]

    def assign_computational_unit(self):
        for instruction in self.instruction_buffer.full_code:
            if instruction.computation_unit is not None:
                continue
            for unit in self.computational_units:
                if instruction.type not in unit.instruction_type:
                    continue
                instruction.computation_unit = unit
                break

    def branch_correction(self):
        instruction = None
        for i in self.instruction_buffer.history:
            if "branch_correction" in i.related_data and i.related_data["branch_correction"]:
                instruction = i
                break

        if instruction is None:
            return

        for i in self.instruction_buffer.history[instruction.counter_index + 1:]:
            i.execution = False
            if i in i.computation_unit.buffer_list:
                i.computation_unit.remove_instruction(i)
            if i.destination is not None and i.destination.startswith("ROB"):
                self.rat.remove_rob(i.destination)

        self.instruction_buffer.pointer = instruction.result
        del instruction.related_data["branch_correction"]

    def issue(self):
        self.assign_computational_unit()
        self.branch_correction()

        peak_instruction = self.instruction_buffer.peak()
        if peak_instruction is None:
            return None
        if peak_instruction.type in peak_instruction.computation_unit.require_rob and self.rat.rob.is_full():
            return None
        if peak_instruction.computation_unit is None:
            Exception(f'"{peak_instruction.type}" instruction has not been implemented by any computational unit')
        if peak_instruction.computation_unit.is_full():
            return None

        instruction = self.instruction_buffer.pop()
        instruction.stage_event.issue = self.get_cycle()
        instruction.computation_unit.decode_instruction(instruction)
        instruction.computation_unit.issue_instruction(instruction)

        # The predictions has been made on the outcome of the branch instruction.
        if instruction.type in self.integer_adder.branch_unit.instruction_type:
            self.instruction_buffer.pointer += self.integer_adder.branch_unit.predict(instruction)

    def execute(self):
        for i in self.computational_units:
            i.step_execute(self.get_cycle())

    def memory(self):
        for i in self.computational_units:
            i.step_memory(self.get_cycle())

    def write_back(self):
        instructions_to_cdb = []
        for unit in self.computational_units:
            if unit.has_result(self.get_cycle()):
                instructions_to_cdb.append(unit.peak_result(self.get_cycle()))

        instructions_to_cdb.sort(key=lambda x: x[0])

        for _, instruction in instructions_to_cdb[:self.parameters["num_cbd"]]:
            instruction.computation_unit.remove_instruction(instruction)

            rob_entry = self.rat.set_rob_value(instruction.destination, instruction.result)
            for instr in self.instruction_buffer.history:
                if rob_entry in instr.operands:
                    instr.operands[instr.operands.index(rob_entry)] = rob_entry.value

            instruction.stage_event.write_back = self.get_cycle()

    def commit(self):
        for instruction in self.instruction_buffer.history:
            if not instruction.execution:
                continue
            if instruction.stage_event.commit is not None and instruction.stage_event.commit[1] < self.get_cycle():
                continue
            if instruction.stage_event.write_back is None:
                return None
            if instruction.stage_event.write_back != "NOP" and instruction.stage_event.write_back >= self.get_cycle():
                return None
            instruction_complete_cycle = instruction.computation_unit.result_event(instruction)
            if instruction_complete_cycle is None or instruction_complete_cycle >= self.get_cycle():
                return None
            instruction.stage_event.commit = (self.get_cycle(), self.get_cycle())
            if instruction.destination != "NOP":
                self.rat.commit_rob(instruction.destination)
            return None

    def step(self):
        self.issue()
        self.execute()
        self.memory()
        self.write_back()
        self.commit()
        self._cycle += 1

    def get_cycle(self) -> int:
        return self._cycle

    def is_working(self):
        if self.instruction_buffer.peak() is not None:
            return True
        if any([not i.is_empty() for i in self.computational_units]):
            return True

        for i in reversed(self.instruction_buffer.history):
            if i.execution and (i.stage_event.commit is None or i.stage_event.commit[1] >= self.get_cycle()):
                return True

        return False

    def run(self):
        while self.is_working():
            self.step()
            if self.get_cycle() > 1e4:
                break
        return self

    def check_asserts(self) -> Tuple[bool, List[AssertResult]]:
        assert_list = []
        for check_key, check_value in self.instruction_buffer.code_asserts.items():
            value = None
            if check_key == "cycle":
                value = self.get_cycle()

            if value is None:
                value = self.rat.get(check_key, raise_error=False)
            if value is None and "mem[" in check_key.lower():
                key = int(check_key.lower()[4:-1])
                value = self.memory_unit.get_value(key)

            append_value = AssertResult(
                result=f"{float(check_value):.4f}" == f"{value:.4f}",
                key=check_key,
                check_value=check_value,
                value=f"{value:.4f}" if isinstance(value, float) else str(value)
            )
            assert_list.append(append_value)
        return all(i.result for i in assert_list), assert_list
