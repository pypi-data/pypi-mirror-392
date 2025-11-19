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
        "Select results folder:",
        choices=result_dirs
    ).ask()
    selected_results_dir = script_dir / selected

    # collect all task runs
    task_run_names = set()
    suffix = "_agent_system_state.pkl"
    for f in selected_results_dir.iterdir():
        if f.is_file() and f.name.endswith(suffix):
            task_run_names.add(f.name[:-len(suffix)])
    task_run_names = list(task_run_names)
    task_run_names.sort()

    # ask user to select task run
    selected_task_run = questionary.select(
        "Select task run:",
        choices=list(task_run_names)
    ).ask()
    selected_results_dir = script_dir / selected

    # print meta-data
    with (selected_results_dir / f"{selected_task_run}_exec_meta_data.json").open("r") as f:
        meta_data = json.load(f)
        pprint(meta_data)

    # print chat history
    with (selected_results_dir / f"{selected_task_run}_log_interface.pkl").open("rb") as f:
        log_interface: LogInterface = pickle.load(f)
        print_logging = bool(questionary.confirm("Print logs", default=True).ask())
        log_interface.print_all_logs(print_logging=print_logging)
