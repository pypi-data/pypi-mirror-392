import argparse
import sys
from datetime import datetime
from pathlib import Path

from benchmarks.ubuntu_bench.utils import TASK_IDS, setup_containers, CONTAINER_AGENTU_DIR, \
    CONTAINER_AGENT_HOME_PATH, _CLIENT

if __name__ == "__main__":
    """
    Runs all sample solutions. 
    Creates containers and executes run_sample_solution.py within them.
    Containers are deleted afterwards.
    """

    parser = argparse.ArgumentParser(description="Run sample solutions - args parser")
    parser.add_argument("-i", "--task-id-first", required=False, default=TASK_IDS[0],
                        help="First task id (int)", type=int)
    parser.add_argument("-j", "--task-id-last", required=False, default=TASK_IDS[-1],
                        help="Last task id (int)", type=int)

    args = parser.parse_args()
    task_ids = range(args.task_id_first, args.task_id_last + 1)
    timestamp = datetime.now().strftime("%m%d-%H%M%S")
    run_sample_solution_script = Path(CONTAINER_AGENTU_DIR) / "benchmark" / "ubuntu_bench" / "run_sample_solution.py"

    # loop over all tasks, setup containers, execute sample solutions, execute validation scripts, delete containers
    for task_id in task_ids:

        # create container
        container = setup_containers(0, [task_id], str(Path.cwd()), timestamp)[0]

        # run run_sample_solutions.py inside container and print output
        exec_id = _CLIENT.api.exec_create(
            container=container.id,
            cmd=f"python {run_sample_solution_script} -t {task_id}",
            environment={"PYTHONPATH": "/opt/agentu"},
            tty=False,  # keep tty off so demux works
            stdin=False,
            workdir=CONTAINER_AGENT_HOME_PATH
        )["Id"]

        for stdout, stderr in _CLIENT.api.exec_start(exec_id, stream=True, demux=True):
            if stdout:
                sys.stdout.write(stdout.decode("utf-8", errors="replace"))
            if stderr:
                sys.stderr.write(stderr.decode("utf-8", errors="replace"))

        exit_code = _CLIENT.api.exec_inspect(exec_id)["ExitCode"]
        container.stop()
        container.remove()
