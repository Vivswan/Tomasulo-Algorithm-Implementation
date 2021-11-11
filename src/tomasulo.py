import ast
import copy
from typing import List

from src.component.computation_units.base_class import ComputationUnit
from src.component.computation_units.float_adder import FloatAdder
from src.component.computation_units.float_multiplier import FloatMultiplier
from src.component.computation_units.integer_adder import IntegerAdder
from src.component.computation_units.memory import Memory
from src.component.instruction_buffer import InstructionBuffer
from src.component.intruction import Instruction
from src.component.registers.rat import RAT
from src.default_parameters import TOMASULO_DEFAULT_PARAMETERS


class Tomasulo:
    _cycle = 1

    def __init__(self, full_code):
        self.instruction_list: List[Instruction] = []
        self.instruction_buffer = InstructionBuffer()
        self.instruction_buffer.append_code(full_code)
        for key, value in self.instruction_buffer.parameters.items():
            if key in TOMASULO_DEFAULT_PARAMETERS:
                parsed_value = ast.literal_eval(value)
                if not isinstance(parsed_value, type(TOMASULO_DEFAULT_PARAMETERS[key])):
                    raise ValueError(
                        f'Invalid type for "{key}"'
                        f', expected: {type(TOMASULO_DEFAULT_PARAMETERS[key])}'
                        f', got: {type(parsed_value)}'
                    )
                TOMASULO_DEFAULT_PARAMETERS[key] = parsed_value

        self.rat = RAT(
            num_integer_register=TOMASULO_DEFAULT_PARAMETERS["num_register"],
            num_float_register=TOMASULO_DEFAULT_PARAMETERS["num_register"],
            num_rob=TOMASULO_DEFAULT_PARAMETERS["num_rob"]
        )

        self.integer_adder = IntegerAdder(
            rat=self.rat,
            latency=TOMASULO_DEFAULT_PARAMETERS["integer_adder_latency"],
            num_rs=TOMASULO_DEFAULT_PARAMETERS["integer_adder_rs"]
        )
        self.float_adder = FloatAdder(
            rat=self.rat,
            latency=TOMASULO_DEFAULT_PARAMETERS["float_adder_latency"],
            num_rs=TOMASULO_DEFAULT_PARAMETERS["float_adder_rs"]
        )
        self.float_multiplier = FloatMultiplier(
            rat=self.rat,
            latency=TOMASULO_DEFAULT_PARAMETERS["float_multiplier_latency"],
            num_rs=TOMASULO_DEFAULT_PARAMETERS["float_multiplier_rs"]
        )
        self.memory_unit = Memory(
            rat=self.rat,
            latency=TOMASULO_DEFAULT_PARAMETERS["memory_unit_latency"],
            latency_mem=TOMASULO_DEFAULT_PARAMETERS["memory_unit_latency_mem"],
            num_rs=TOMASULO_DEFAULT_PARAMETERS["memory_unit_rs"]
        )
        self.computational_units: List[ComputationUnit] = [
            self.integer_adder,
            self.float_adder,
            self.float_multiplier,
            self.memory_unit,
        ]

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
            if i in i.computation_unit.buffer_list:
                i.computation_unit.remove_instruction(i)
            if i.destination is not None and i.destination.startswith("ROB"):
                self.rat.remove_rob(i.destination)
            i.execution = False

        self.instruction_buffer.pointer = instruction.result
        del instruction.related_data["branch_correction"]

    def issue(self):
        self.assign_computational_unit()
        self.branch_correction()

        peak_instruction = self.instruction_buffer.peak()
        if peak_instruction is None:
            return None
        if peak_instruction.type in peak_instruction.computation_unit.require_rob:
            if self.rat.rob.is_full():
                return None

        # Makes a Copy of the RAT Table and stores it with the branch instruction
        instruction = self.instruction_buffer.pop()
        instruction.related_data["rat_copy"] = copy.deepcopy(self.rat)

        # The predictions has been made on the outcome of the branch instruction.
        if instruction.type in self.integer_adder.branch_unit.instruction_type:
            self.instruction_buffer.pointer += self.integer_adder.branch_unit.predict(instruction)

        # this figures out which computational unit the instruction goes to.
        if instruction.computation_unit is None:
            Exception(f'"{instruction.type}" instruction has not been implemented by any computational unit')

        if instruction.computation_unit.is_full():
            return None

        instruction.computation_unit.decode_instruction(instruction)
        instruction.stage_event.issue = self._cycle
        instruction.computation_unit.issue_instruction(instruction)

    def execute(self):
        for i in self.computational_units:
            i.step(self._cycle)

    def write_back(self):
        compute_unit = []
        for i in self.computational_units:
            if i.has_result(self._cycle):
                for j in i.peak_result(self._cycle):
                    compute_unit.append((j.stage_event.execute[1], i, j))

        compute_unit.sort(key=lambda x: x[0])

        for i in compute_unit[:TOMASULO_DEFAULT_PARAMETERS["num_cbd"]]:
            instruction = i[2]
            i[1].remove_instruction(instruction)

            if instruction.destination == "NOP":
                continue

            rob_entry = self.rat.set_rob_value(instruction.destination, instruction.result)

            for instr in self.instruction_buffer.full_code:
                if rob_entry in instr.operands:
                    instr.operands[instr.operands.index(rob_entry)] = rob_entry.value

            instruction.stage_event.write_back = self._cycle

    def commit(self):
        instruction = None
        for instr in self.instruction_buffer.history:
            if not instr.execution:
                continue
            if instr.stage_event.commit is not None:
                if instr.stage_event.commit[1] >= self._cycle:
                    break
                else:
                    continue
            if instr.stage_event.write_back is not None:
                if instr.stage_event.write_back == "NOP":
                    instruction = instr
                elif instr.stage_event.write_back < self._cycle:
                    instruction = instr
                    self.rat.commit_rob(instr.destination)
            break

        if instruction is None:
            return None

        instruction.stage_event.commit = (self._cycle, self._cycle)

    def step(self):
        self.issue()
        self.execute()
        self.write_back()
        self.commit()
        self._cycle += 1

    def get_cycle(self) -> int:
        return self._cycle

    def is_working(self):
        # TODO
        return self.instruction_buffer.peak() is not None


if __name__ == '__main__':
    code = """
        # ADD R1, R2, R3 
        # SUB R1, R1, R3 
        # ADDI R1, R2, 5
        # ADDD F1, F2, F3 
        # SUB.D F1, F2, F3 
        # SUBi R1, R2, 5

        # LD R1 0(R2) 
        # LD R1 0(R2) 
        LD R1 0(R2) 
        # ADDI R1, R2, 5
        SD R1 8(R2) 
        ADDI R1, R2, 5
        LD R1 8(R2) 
        LD R1 8(R2) 
        # BEQ R1, R2, 2
        # BNE R1, R2, 
    """
    tomasulo = Tomasulo(code)
    while tomasulo._cycle < 500:
        tomasulo.step()
    print()
    for k in tomasulo.instruction_buffer.history:
        print(k)
    print()
    # tomasulo.rat.print_tables()
