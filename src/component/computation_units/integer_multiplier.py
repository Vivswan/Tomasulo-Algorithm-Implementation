from src.component.computation_units.base_class import ComputationUnit
from src.component.events import processor_status
from src.component.intruction import Instruction, InstructionType

class IntegerMultiplier (ComputationUnit):
    instruction_type = [InstructionType.MUl]