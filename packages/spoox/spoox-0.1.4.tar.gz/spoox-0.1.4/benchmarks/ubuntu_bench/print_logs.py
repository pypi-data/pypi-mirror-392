import json
import pickle
import re
import sys
from pathlib import Path
from pprint import pprint

import questionary

from spoox.interface.LogInterface import LogInterface


if __name__ == "__main__":

    # scan current directory for result folders
    script_dir = Path(__file__).resolve().parent
    pattern = re.compile(r"^results_.*")
    result_dirs = []
    for entry in script_dir.iterdir():
        if entry.is_dir() and pattern.match(entry.name):
            result_dirs.append(entry.name)
    if not result_dirs:
        print("No benchmark result directories found.")
        sys.exit(0)

    # ask user to select benchmark results
    selected = questionary.select(
        "Select benchmark run results:",
        choices=result_dirs
    ).ask()
    selected_results_dir = script_dir / selected

    # load benchmark run meta-data
    with (selected_results_dir / f"ubuntu_bench_run_meta_data.pkl").open("rb") as f:
        meta_data = pickle.load(f)
    pprint(meta_data)

    # ask user to select benchmark run and task
    selected_run = questionary.select(
        "Select specific run:",
        choices=[str(r) for r in range(1, meta_data["runs"] + 1)]
    ).ask()
    selected_task = questionary.select(
        "Select specific task:",
        choices=[str(t) for t in meta_data["task_ids"]]
    ).ask()

    # print meta-data
    with (selected_results_dir / f"run_{selected_run}_task_{selected_task}_exec_meta_data.json").open("r") as f:
        meta_data = json.load(f)
        pprint(meta_data)

    # print chat history
    with (selected_results_dir / f"run_{selected_run}_task_{selected_task}_log_interface.pkl").open("rb") as f:
        log_interface: LogInterface = pickle.load(f)
        print_logging = bool(questionary.confirm("Print logs", default=True).ask())
        log_interface.print_all_logs(print_logging=print_logging)
