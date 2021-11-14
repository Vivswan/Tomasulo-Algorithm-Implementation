import copy
import re
from enum import Enum
from typing import List, Union, TypeVar, Generic

from src.helper.strike import strike
from src.instruction.events import StageEvent

T = TypeVar('T')
operand_types = Union[str, int, float, bool]


class InstructionType(Enum):
    # Data Transfer Instructions
    LD = "LD"
    SD = "SD"

    # Control Transfer Instructions
    BEQ = "BEQ"
    BNE = "BNE"

    # ALU Instructions
    ADD = "ADD"
    SUB = "SUB"

    ADDI = "ADDI"
    SUBI = "SUBI"

    ADDD = "ADDD"
    SUBD = "SUBD"

    MULTD = "MULTD"
    DIVD = "DIVD"


class Instruction(Generic[T]):
    def __init__(self, instruction_str: str, index):
        instruction_str = instruction_str.strip()
        instruction_type = instruction_str.split(" ")[0].replace(".", "").upper()
        operands = re.split(' |\(|\)|,', instruction_str)[1:]
        operands = [i for i in operands if len(i) > 0]

        if not hasattr(InstructionType, instruction_type):
            raise Exception(f'Invalid instruction type: "{instruction_type}"')

        self.instruction: str = instruction_str

        self.counter_index: int = -1
        self.index: int = index
        self.execution: bool = True
        self.computation_unit: 'ComputationUnit' = None

        self.type: InstructionType = getattr(InstructionType, instruction_type)
        self.operands: List[operand_types] = operands
        self.stage_event = StageEvent()
        self.result: T = None
        self.destination: str = None

        self.prev: 'Instruction' = None
        self.related_data: dict = {}

    def __repr__(self):
        result = str(self.index).ljust(3)
        result += " " + str(self.counter_index).ljust(3)
        result += " " + self.instruction
        result += f", unit={self.computation_unit.__class__.__name__}"
        result += f", execution={self.execution}"
        result += f", result={self.result}"

        result += f", event=[{self.stage_event}]"
        result += f", destination={self.destination}"
        result += f", operands={self.operands}"
        if self.type in [InstructionType.BEQ, InstructionType.BNE]:
            result += f", prediction ({self.related_data['branch_prediction_accurate']})" \
                      f": {'branch' if self.related_data['branch_jump'] else 'continue'}"

        if self.type in [InstructionType.LD, InstructionType.SD]:
            result += f", address: {self.related_data['memory_address']}"
        if self.execution:
            return result
        else:
            return strike(result)


def create_copy_instruction(instruction: Instruction) -> Instruction:
    result = copy.deepcopy(instruction)
    result.computation_unit = instruction.computation_unit
    return result


def print_str_instructions(instructions: List[Instruction]):
    rows = [
        [
            "",
            "Counter",
            "Index",
            "Instruction",
            "Issue",
            "Execute",
            "Memory",
            "Write Back",
            "Commit",
            "Result",
            "Operands",
        ]
    ]
    strike_row = [True]

    for i, v in enumerate(instructions):
        row = [
            "" if v.execution else "~",
            v.counter_index,
            v.index,
            v.instruction,
            v.stage_event.issue if v.stage_event.issue != "NOP" else "",
            v.stage_event.execute if v.stage_event.execute != "NOP" else "",
            v.stage_event.memory if v.stage_event.memory != "NOP" else "",
            v.stage_event.write_back if v.stage_event.write_back != "NOP" else "",
            v.stage_event.commit if v.stage_event.commit != "NOP" else "",
            v.result,
            v.operands if v.execution else "",
        ]
        strike_row.append(v.execution)
        row = [str(ii) for ii in row]
        rows.append(row)

    lengths = [0] * len(rows[0])
    for i in rows:
        for j, v in enumerate(i):
            if lengths[j] < len(str(v)):
                lengths[j] = len(str(v)) + 4

    lengths[0] -= 2
    lengths[rows[0].index("Instruction")] += 6

    format_str = "".join(["{:<" + str(i) + "}" for i in lengths])
    result_str = ""
    for i, v in enumerate(rows):
        r = format_str.format(*v)
        result_str += (r if strike_row[i] else strike(r)) + "\n"
    return result_str
