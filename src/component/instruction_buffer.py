from typing import List, Union

from src.component.intruction import Instruction


class InstructionBuffer:
    def __init__(self):
        self.full_code: List[Instruction] = []
        self.counter = 0
        self.pointer: int = 0
        self.history: List[Instruction] = []

    def append_code(self, code_str: str):
        parser_code = []
        for line in code_str.split("\n"):
            line = line.strip()

            if len(line) == 0:
                continue

            if line.startswith("#"):
                continue

            parser_code.append(Instruction(line, index=len(parser_code) + len(self.full_code)))
        self.full_code += parser_code
        return self

    def peak(self) -> Union[None, Instruction]:
        if self.pointer >= len(self.full_code):
            return None
        return self.full_code[self.pointer]

    def pop(self) -> Union[None, Instruction]:
        if self.peak() is None:
            return None
        instr = Instruction(self.peak().instruction, self.peak().index)
        instr.counter_index = self.counter
        self.pointer += 1
        self.counter += 1
        self.history.append(instr)
        return instr
