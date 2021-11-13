import copy
import re
from enum import Enum
from typing import List, Union, TypeVar, Generic

# from src.component.computation_units.base_class import ComputationUnit
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
        self.computation_unit: 'ComputationUnit' = None
        self.counter_index: int = -1
        self.index: int = index
        self.execution: bool = True

        # issue
        self.branch_jump: bool = None
        self.branch_prediction_accurate: bool = None  # placeholder

        self.type: InstructionType = getattr(InstructionType, instruction_type)
        self.operands: List[operand_types] = operands
        self.stage_event = StageEvent()
        self.result: T = None
        self.destination: str = None
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
            result += f", prediction ({self.branch_prediction_accurate})" \
                      f": {'branch' if self.branch_jump else 'continue'}"
        return result


def create_copy_instruction(instruction):
    result = copy.deepcopy(instruction)
    result.computation_unit = instruction.computation_unit
    return result
