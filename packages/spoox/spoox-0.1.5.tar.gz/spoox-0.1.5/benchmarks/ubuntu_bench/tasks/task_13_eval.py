import re
import sys
from pathlib import Path

if __name__ == "__main__":

    home = Path("/home/linus")
    benchmark_copy_dir = home / "bench"
    number_of_tasks_sol_file = home / "number_of_tasks.txt"

    # count available tasks
    pattern = re.compile(r"^task_(\d+)_desc\.txt$")
    numbers = {
        int(match.group(1))
        for file in benchmark_copy_dir.iterdir()
        if (match := pattern.match(file.name))
    }

    # check 'number_of_tasks' solution file and validate content
    if not number_of_tasks_sol_file.is_file():
        sys.exit("Missing number_of_tasks.txt")
    with number_of_tasks_sol_file.open() as f:
        content = f.read().strip()
        if content != f"{len(numbers)}":
            sys.exit("Incorrect total number of tasks")

    sys.exit(0)
