import re
from enum import Enum
from typing import List, Union, TypeVar, Generic

from src.component.events import StageEvent

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
    instruction: str
    counter_index: int
    type: InstructionType
    operands: List[operand_types]
    stage_event: StageEvent
    result: T
    destination: str
    related_data: dict

    def __init__(self, instr_str: str, index):
        instr_type = instr_str.split(" ")[0].replace(".", "").upper()
        operands = re.split(' |\(|\)|,', instr_str)[1:]
        operands = [i for i in operands if len(i) > 0]

        if not hasattr(InstructionType, instr_type):
            raise Exception(f'Invalid instruction type: "{instr_type}"')

        self.instruction = instr_str
        self.counter_index = -1
        self.index = index
        self.execution = True

        # issue
        self.branch_jump = None
        self.branch_prediction_accurate = None  # placeholder

        self.type = getattr(InstructionType, instr_type)
        self.operands = operands
        self.stage_event = StageEvent()
        self.result = None
        self.destination = None
        self.related_data = {}

    def __repr__(self):
        result = str(self.index).ljust(3)
        result += " " + str(self.counter_index).ljust(3)
        result += " " + self.instruction
        result += f", result={self.result}"
        result += f", event=[{self.stage_event}]"
        result += f", destination={self.destination}"
        result += f", operands={self.operands}"
        if self.type in [InstructionType.BEQ, InstructionType.BNE]:
            result += f", prediction ({self.branch_prediction_accurate})" \
                      f": {'branch' if self.branch_jump else 'continue'}"
        return result
