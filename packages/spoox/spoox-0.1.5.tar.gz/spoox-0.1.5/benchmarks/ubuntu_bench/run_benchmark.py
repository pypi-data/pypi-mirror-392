import argparse
import os
import pickle
from datetime import datetime
from pathlib import Path

import questionary
from docker.models.containers import Container
from rich.console import Console
from rich.live import Live

from benchmarks.ubuntu_bench.utils import CONTAINER_AGENTU_RESULTS_PATH, \
    CONTAINER_AGENT_RUNNABLE_PATH, CONTAINER_AGENTU_DIR, CONTAINER_AGENT_HOME_PATH, setup_containers, TASK_IDS, \
    _CLIENT, make_table


def run_containers(run_id: int, agent_id: str, task_ids: [int], model_id: str, cs: [Container], feedback_iterations_max: int = 0,
                   vague_descriptions: bool = False, delete: bool = False) -> None:
    """Trigger agent with the corresponding container task."""

    for c_idx, c in enumerate(cs):

        # setup container execution
        task_id = task_ids[c_idx]
        exec_id = _CLIENT.api.exec_create(
            container=c.id,
            cmd=f"python {CONTAINER_AGENT_RUNNABLE_PATH} "
                f"-i {run_id} "
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
            stdin=False,
        )["Id"]

        # start container and read stream
        out_lines = []
        console = Console()
        with Live(make_table(out_lines), console=console, refresh_per_second=1, transient=True) as live:
            try:
                stream = _CLIENT.api.exec_start(exec_id, stream=True, demux=True)
                for stdout, stderr in stream:
                    if stdout:
                        out_lines.append(stdout.decode(errors="replace"))
                        live.update(make_table(out_lines, ))
                    if stderr:
                        out_lines.append(stderr.decode(errors="replace"))
                        live.update(make_table(out_lines, ))
            finally:
                pass
        # get exit code and stop container
        exit_code = _CLIENT.api.exec_inspect(exec_id)["ExitCode"]
        c.stop()
        if delete:
            c.remove()

        # logging
        output_last_line = str(out_lines[-1].strip().splitlines()[-1]).lower()
        if exit_code != 0:
            questionary.print(f"-> failure run: {run_id:02} - task: {task_id:03} - error:\n\n{'\n'.join(out_lines)}",
                              style="fg:red")
        elif 'min - success' in output_last_line:
            questionary.print(output_last_line, style="fg:green")
        else:
            questionary.print(output_last_line, style="fg:orange")


# example usage:
# python src/benchmark/ubuntu_bench/run_benchmark.py -r 1 -a mas-group-chat-m -m gpt-oss:20b -i 1 -j 10
if __name__ == '__main__':

    # parse and check CLI args
    parser = argparse.ArgumentParser(description="Run benchmark - args parser")
    parser.add_argument("-r", "--runs", required=True,
                        help="Number of benchmark runs (int)", type=int)
    parser.add_argument("-a", "--agent-id", required=False, default="singleton", help="Agent id (str)", type=str)
    parser.add_argument("-m", "--model-id", required=False, default="qwen3:14b", help="Model id (str)", type=str)
    parser.add_argument("-v", "--vague-descriptions", default=False, action="store_true",
                        help="Run vague task descriptions")
    parser.add_argument("-f", "--feedback-iterations-max", required=False, default=0, type=int,
                        help="Max number of feedback iterations ('eval file outputs back to agent'); default 0 (int)")
    parser.add_argument("-d", "--delete-containers", default=False, action="store_true",
                        help="Delete all containers after benchmark run")
    parser.add_argument("-i", "--task-id-first", required=False, default=TASK_IDS[0],
                        help="First task id (int)", type=int)
    parser.add_argument("-j", "--task-id-last", required=False, default=TASK_IDS[-1],
                        help="Last task id (int)", type=int)

    args = parser.parse_args()
    runs = args.runs
    model_id = str(args.model_id) + "-docker"
    task_ids = range(args.task_id_first, args.task_id_last + 1)

    if runs <= 0:
        raise ValueError("Number of benchmark runs must be greater than 0.")
    if any(i not in TASK_IDS for i in task_ids):
        raise ValueError("Not all task_ids are available/exist.")

    # create results directory on host machine
    current_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_dir_name = f"results_{timestamp}_{args.agent_id}_{args.model_id.replace(":", "-")}_v-{args.vague_descriptions}_f-{args.feedback_iterations_max}_d-{args.delete_containers}"
    results_dir_path = Path(current_dir) / results_dir_name
    results_dir_path.mkdir(parents=True, exist_ok=True)

    # save benchmark meta-data in a pickle file
    with (results_dir_path / f"ubuntu_bench_run_meta_data.pkl").open("wb") as f:
        exec_meta_data = {
            "runs": args.runs,
            "task_ids": task_ids,
            "agent": args.agent_id,
            "model": args.model_id,
            "vague_description": args.vague_descriptions,
            "feedback_iterations_max": args.feedback_iterations_max,
            "delete_containers": args.delete_containers,
        }
        pickle.dump(exec_meta_data, f)

    # run benchmark
    for r in range(1, runs + 1):
        containers = setup_containers(r, task_ids, str(results_dir_path), datetime.now().strftime("%m%d-%H%M%S"))
        run_containers(r, args.agent_id, task_ids, model_id, containers, args.feedback_iterations_max,
                       args.vague_descriptions, args.delete_containers)

