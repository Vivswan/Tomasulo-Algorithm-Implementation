from dataclasses import dataclass
from typing import List, Union, Any, TypeVar, Generic

from src.component.events import StageEvent

T = TypeVar('T')
operand_types = Union[str, int, float, bool]


class InstructionType:
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


@dataclass
class Instruction(Generic[T]):
    instruction: str
    type: InstructionType
    operands: List[operand_types]
    stage_event: StageEvent
    result: T


def parse_instruction(instr_line: str) -> Instruction:
    pass
