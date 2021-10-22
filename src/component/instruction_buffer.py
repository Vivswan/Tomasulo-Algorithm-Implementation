from typing import List

from src.component.intruction import Instruction, parse_instruction


class InstructionBuffer:
    full_code: List[Instruction]
    buffer: List[Instruction]

    def __init__(self, code: str, buffer_len):
        self.full_code = []
        code = code.split("\n")
        for line in code:
            line = line.strip()
            if len(line) == 0:
                continue

            self.full_code.append(parse_instruction(line))



    def peak(self) -> Instruction:

        pass

    def pop(self) -> Instruction:
        pass

    def step(self):
        pass

    def clear(self):
        pass


if __name__ == '__main__':
    code = """
        LD R1 0(R2) 
        ADD R1, R1, R3 
        SD R1, 0(R2) 
        ADD R2, R2, 8 
        BNE R2, R4, Loop
    """
    ib = InstructionBuffer(code, 5)
    print(ib.full_code)