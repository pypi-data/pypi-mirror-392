import sys
from pathlib import Path

if __name__ == "__main__":

    home = Path("/home/linus")
    code_file = home / "all_code.py"
    count_file = home / "function_count.txt"

    # check code file exists and read it
    if not count_file.is_file():
        sys.exit("Missing all_code.py")
    with code_file.open() as f:
        code_lines = f.readlines()

    # check that there is exactly one function definition
    func_lines = [line for line in code_lines if line.strip().startswith("def ")]
    if len(func_lines) != 1:
        sys.exit(f"Error: Expected 1 function definition, found {len(func_lines)}.")

    # check that all python code snippets were copied
    py_cp_t1 = any("def add(a, b)" in l for l in code_lines)
    py_cp_t2 = any("return a + b" in l for l in code_lines)
    py_cp_t3 = any("for i in range(5):" in l for l in code_lines)
    py_cp_t4 = any("print(i)" in l for l in code_lines)
    if not py_cp_t1 or not py_cp_t2 or not py_cp_t3 or not py_cp_t4:
        sys.exit(f"Not all python snippets were copied to all_code.py.")

    # make sure that only code snippets of html files were copied
    py_cp_t5 = any("if 5 > 4:" in l for l in code_lines)
    py_cp_t6 = any("print('comparison worked')" in l for l in code_lines)
    if py_cp_t5 or py_cp_t6:
        sys.exit(f"Some python snippets were copied to all_code.py that are not part of a html file.")

    # check function count file and validate content
    if not count_file.is_file():
        sys.exit("Missing function_count.txt")
    with count_file.open() as f:
        content = f.read().strip()
        if content != "1":  # Only one function defined across snippets
            sys.exit("Incorrect function count")

    sys.exit(0)
