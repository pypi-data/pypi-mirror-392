import argparse
import json
import os
import pickle
from datetime import datetime
from pathlib import Path
from pprint import pprint

import questionary
from rich.console import Console
from rich.live import Live

from benchmarks.ubuntu_bench.utils import TASK_IDS, setup_containers, AVAILABLE_AGENT_IDS, AVAILABLE_AGENT_MODELS, \
    CONTAINER_AGENT_RUNNABLE_PATH, CONTAINER_AGENTU_DIR, \
    CONTAINER_AGENTU_RESULTS_PATH, CONTAINER_AGENT_HOME_PATH, _CLIENT, make_table
from spoox.interface.LogInterface import LogInterface


def select_agent() -> str:
    """ask user to select agent"""
    return questionary.select(
        "Select agent",
        choices=AVAILABLE_AGENT_IDS
    ).ask()


def select_task() -> int:
    """ask user to select a task"""
    while True:
        try:
            t = int(questionary.text("Select task (int)", default="1").ask())
            if t in TASK_IDS:
                return t
        except:
            pass


def select_model():
    """ask user to select model"""
    return questionary.select(
        "Select model",
        choices=AVAILABLE_AGENT_MODELS
    ).ask()


def select_vague_description() -> bool:
    """ask user if the vague description should be used"""
    return bool(questionary.confirm("Vague description", default=False).ask())


def select_feedback_iterations_max() -> int:
    """ask user to select the feedback iteration max"""
    while True:
        try:
            t = int(questionary.text("Select feedback iteration max (int)", default="0").ask())
            if t >= 0:
                return t
        except:
            pass


def select_delete_containers() -> bool:
    """ask user containers should be deleted"""
    return bool(questionary.confirm("Delete docker containers", default=True).ask())


def select_print_logs() -> bool:
    """ask user if logs should be printed as well"""
    return bool(questionary.confirm("Print logs", default=True).ask())


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run agent once - args parser")
    parser.add_argument("-a", "--agent-id", required=False, help="Agent id (str)", type=str)
    parser.add_argument("-t", "--task-id", required=False, help="Task id (int)", type=int)
    parser.add_argument("-m", "--model-id", required=False, help="Model id (str)", type=str)
    parser.add_argument("-v", "--vague-descriptions", default=None, action="store_true",
                        help="Run vague task descriptions")
    parser.add_argument("-f", "--feedback-iterations-max", required=False, type=int,
                        help="Max number of feedback iterations ('eval file outputs back to agent'); default 0 (int)")
    parser.add_argument("-d", "--delete-containers", default=None, action="store_true",
                        help="Delete all containers after benchmark run")

    # make sure agent, task, etc, are selected
    args = parser.parse_args()
    agent_id = select_agent() if args.agent_id is None else args.agent_id
    task_id = select_task() if args.task_id is None else args.task_id
    model_id = select_model() if args.model_id is None else args.model_id
    vague_descriptions = select_vague_description() if args.vague_descriptions is None else args.vague_descriptions
    feedback_iterations_max = select_feedback_iterations_max() if args.feedback_iterations_max is None else args.feedback_iterations_max
    del_containers = select_delete_containers() if args.delete_containers is None else args.delete_containers

    # create results directory on host machine
    current_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime("%m%d-%H%M%S")
    results_dir_name = f"results_single_task_results"
    results_dir_path = Path(current_dir) / results_dir_name
    results_dir_path.mkdir(parents=True, exist_ok=True)

    # run agent and task and log stream
    # setup container
    container = setup_containers(0, [task_id], str(results_dir_path), timestamp)[0]
    exec_id = _CLIENT.api.exec_create(
        container=container.id,
        cmd=f"python {CONTAINER_AGENT_RUNNABLE_PATH} "
            f"-i {0} "
            f"-t {task_id} "
            f"-g {agent_id} "
            f"-m {model_id} "
            f"-a {CONTAINER_AGENTU_DIR} "
            f"-r {CONTAINER_AGENTU_RESULTS_PATH} "
            f"-o {CONTAINER_AGENT_HOME_PATH} "
            f"{'-v ' if vague_descriptions else ''}"
            f"-f {feedback_iterations_max}",
        environment={"PYTHONPATH": "/opt/agentu"},
        tty=False,  # keep tty off so demux works
        stdin=False
    )["Id"]
    # start container and read stream
    out_lines = []
    console = Console()
    with Live(make_table(out_lines), console=console, refresh_per_second=1, transient=True) as live:
        for stdout, stderr in _CLIENT.api.exec_start(exec_id, stream=True, demux=True):
            if stdout:
                out_lines.append(stdout.decode(errors="replace"))
                live.update(make_table(out_lines))
            if stderr:
                out_lines.append(stderr.decode(errors="replace"))
                live.update(make_table(out_lines))
    # get exit code and stop container
    exit_code = _CLIENT.api.exec_inspect(exec_id)["ExitCode"]
    container.stop()
    if del_containers:
        container.remove()

    # logging
    output_last_line = str(out_lines[-1].strip().splitlines()[-1]).lower()
    if exit_code != 0:
        questionary.print(f"-> error run: 0 - task: {task_id:03} - error:\n\n{'\n'.join(out_lines)}", style="fg:red")
    elif 'min - success' in output_last_line:
        questionary.print(output_last_line, style="fg:green")
    else:
        questionary.print(output_last_line, style="fg:orange")

    # print meta-data
    with (results_dir_path / f"run_0_task_{task_id}_exec_meta_data.json").open("r") as f:
        meta_data = json.load(f)
        pprint(meta_data)

    # print chat history
    with (results_dir_path / f"run_0_task_{task_id}_log_interface.pkl").open("rb") as f:
        log_interface: LogInterface = pickle.load(f)
        print_logging = select_print_logs()
        log_interface.print_all_logs(print_logging=print_logging)
