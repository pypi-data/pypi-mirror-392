import argparse
import subprocess
import sys


if __name__ == "__main__":
    """
    Executes the sample solution and the evaluation afterwards for the given task. 
    Should be executed inside the correct task container.
    """

    parser = argparse.ArgumentParser(description="Run sample solutions - args parser")
    parser.add_argument("-t", "--task-id", required=True, help="Task id (int)", type=int)

    args = parser.parse_args()
    task_id = args.task_id
    tasks_dir = "/opt/agentu/src/benchmark/ubuntu_bench/tasks"

    # execute sample solution
    setup_out = ""
    try:
        result = subprocess.run(
            ["bash", f"{tasks_dir}/task_{task_id}_sol.sh"],
            capture_output=True,
            text=True,
            check=True,
            cwd="/home/linus",
            user='linus'
        )
        if result.returncode != 0:
            print(f"Failed: Sample solution script for task {task_id}:\n{result.stdout}\n{result.stderr}")
            sys.exit(result.returncode)
        print(f"Success: Sample solution script for task {task_id}.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Sample solution script for task {task_id}:\n{e}\n{e.stdout}\n{e.stderr}")
        sys.exit(1)

    # run evaluation script
    eval_out = ""
    try:
        result = subprocess.run(
            ["python", f"{tasks_dir}/task_{task_id}_eval.py"],
            capture_output=True,
            text=True,
            check=True,
            cwd='/home/linus',
            user='linus'
        )
        if result.returncode != 0:
            print(f"Failed: Evaluation script for task {task_id}: \n{result.stdout}")
            sys.exit(result.returncode)
        print(f"Success: Evaluation script for task {task_id}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed: Evaluation script for task {task_id}: \n{e} \n{e.stderr} \n{e.stdout}")
        sys.exit(1)

    sys.exit(0)
