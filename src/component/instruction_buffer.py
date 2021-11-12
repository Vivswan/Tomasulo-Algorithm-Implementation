from typing import List, Union, Dict

from src.component.instruction import Instruction, create_copy_instruction


class InstructionBuffer:
    def __init__(self):
        self.full_code: List[Instruction] = []
        self.counter = 0
        self.pointer: int = 0
        self.history: List[Instruction] = []
        self.code_pointers = {}

        self.code_parameters: Dict[str, str] = {}
        self.code_asserts: Dict[str, str] = {}

    def append_code(self, code_str: str):
        parser_code = []
        for line in code_str.split("\n"):
            line = line.strip()

            if len(line) == 0:
                continue

            if line.startswith("#"):
                continue

            if line.startswith("$") or line.startswith("!"):
                if len(self.full_code) > 0:
                    raise Exception(f"{line[0]} should be before all instructions")

                save_location = {}
                if line.startswith("$"):
                    save_location = self.code_parameters
                if line.startswith("!"):
                    save_location = self.code_asserts

                line = line[1:].strip()
                if "=" in line:
                    [key, value] = line.split("=")
                    save_location[key.strip()] = value.strip()
                continue

            index = len(parser_code) + len(self.full_code)
            if ":" in line:
                [label, line] = line.split(":")
                line = line.strip()
                label = label.strip()
                self.code_pointers[label] = index

            for key, value in self.code_pointers.items():
                if key in line:
                    line = line.replace(key, str(value - index - 1))

            instruction = Instruction(line, index=index)
            parser_code.append(instruction)
        self.full_code += parser_code
        return self

    def peak(self) -> Union[None, Instruction]:
        if self.pointer >= len(self.full_code):
            return None
        return self.full_code[self.pointer]

    def pop(self) -> Union[None, Instruction]:
        if self.peak() is None:
            return None
        instr = create_copy_instruction(self.peak())
        instr.counter_index = self.counter
        self.pointer += 1
        self.counter += 1
        self.history.append(instr)
        return instr
