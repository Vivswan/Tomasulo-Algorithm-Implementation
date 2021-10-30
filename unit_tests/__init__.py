import os
import pathlib

test_codes = {}
path = pathlib.Path(__file__).parent.resolve()

for filename in os.listdir(path):
    if filename.startswith("test_") and filename.endswith(".txt"):
        with open(path.joinpath(filename), "r") as file:
            test_codes[int(filename[5:][:-4])] = file.read()
