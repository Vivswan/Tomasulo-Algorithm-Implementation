from typing import List, Union

from src.component.intruction import Instruction


class InstructionBuffer:
    full_code: List[Instruction]
    buffer: List[Instruction]
    buffer_limit: int
    buffer_code_index: int

    def __init__(self, buffer_limit):
        self.full_code = []
        self.buffer = []
        self.buffer_limit = buffer_limit
        self.buffer_code_index = 0

    def append_code(self, code_str: str):
        parser_code = []
        for line in code_str.split("\n"):
            line = line.strip()

            if len(line) == 0:
                continue

            if line.startswith("#"):
                continue

            parser_code.append(Instruction(line))

        self.full_code += parser_code
        self.step()
        return self

    def peak(self) -> Union[None, Instruction]:
        if len(self.buffer) == 0:
            return None

        return self.buffer[0]

    def pop(self) -> Union[None, Instruction]:
        if len(self.buffer) == 0:
            return None

        return self.buffer.pop(0)

    def step(self):
        while len(self.buffer) < self.buffer_limit and self.buffer_code_index < len(self.full_code):
            self.buffer.append(self.full_code[self.buffer_code_index])
            self.buffer_code_index += 1
