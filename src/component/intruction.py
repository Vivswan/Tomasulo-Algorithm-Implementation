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
    type: InstructionType
    operands: List[operand_types]
    stage_event: StageEvent
    result: T = None
    destination: str

    def __init__(self, instr_str: str):
        instr_type = instr_str.split(" ")[0].replace(".", "").upper()
        operands = re.split(' |\(|\)|,', instr_str)[1:]
        operands = [i for i in operands if len(i) > 0]

        if not hasattr(InstructionType, instr_type):
            raise Exception(f'Invalid instruction type: "{instr_type}"')

        self.instruction = instr_str
        self.type = getattr(InstructionType, instr_type)
        self.operands = operands
        self.stage_event = StageEvent()
        self.result = None
        self.destination = None

    def __repr__(self):
        return f"{self.instruction}: operands={self.operands}, destination={self.destination}, result={self.result}, event=[{self.stage_event}]"
