import argparse
import asyncio
import subprocess
import time
from pathlib import Path

import questionary
from dotenv import load_dotenv

from spoox.environment.LocalEnvironment import LocalEnvironment
from spoox.interface.LogInterface import LogInterface
from spoox.utils import setup_model_client, setup_agent_system, save_logs


"""
isolated testing:
docker run --rm -v ./:/opt/agentu/benchmark_results ubuntu-bench bash -c "python3 \"/opt/agentu/src/benchmark/ubuntu_bench/run_agent.py\" -i 0 -t \"1\" -g \"singleton\" -m \"gpt-oss:20b\" -a \"/opt/agentu/src\" -r \"/opt/agentu/benchmark_results\" -o \"/home/linus\" -v False -f 0"
sudo env PYTHONPATH=/opt/agentu python3 "/opt/agentu/src/benchmark/ubuntu_bench/run_agent.py" -i 0 -t "1" -g "singleton" -m "gpt-oss:20b" -a "/opt/agentu/src" -r "/opt/agentu/benchmark_results" -o "/home/linus" -v False -f 0
"""


def run_agent(task_id: str, run_id: int, agent_id: str, model_id: str, results_dir_path: Path, agent_dir_path: Path,
              tasks_dir_path: Path, home_dir_path: Path, feedback_iterations_max: int, vague_descriptions: bool) -> (
        bool, str):

    load_dotenv(dotenv_path=str(agent_dir_path / ".env"))

    # load task description
    task_descr_path = tasks_dir_path / f"task_{task_id}_desc{'_vague' if vague_descriptions else ''}.txt"
    with task_descr_path.open() as file:
        task_descr = file.read()

    # setup interface
    log_interface = LogInterface(
        logging_active=True,
        feedback_iterations_max=feedback_iterations_max,
        eval_file_path=str(tasks_dir_path / f"task_{task_id}_eval.py"),
        home_dir_path=str(home_dir_path),
    )
    # pass task and then always exit after agents answer
    log_interface.user_delegate.user_input = [task_descr, 'q']
    # always confirm shell tool execution
    log_interface.user_delegate.default_user_choice = 'confirm'

    # setup environment
    environment = LocalEnvironment()

    # setup model client (llm, chat completion model)
    if model_id[-6:] == 'docker':
        model_client = setup_model_client(model_id=model_id[:-7], docker_access=True)
    else:
        model_client = setup_model_client(model_id=model_id)

    # setup and run agent
    agent = setup_agent_system(agent_id, model_client, environment, log_interface)
    start_time = time.time()
    try:
        asyncio.run(agent.start())
    except Exception as e:
        log_interface.print(str(e), f"Exception during agent system execution.")
    exec_minutes = (time.time() - start_time) / 60

    # evaluate task
    eval_success = False
    eval_out = ""
    try:
        result = subprocess.run(
            ["python", str(tasks_dir_path / f"task_{task_id}_eval.py")],
            capture_output=True,
            text=True,
            check=True,
            cwd=home_dir_path,
            user='linus'
        )
        eval_out += f"{result.stdout.strip()}" if result.stdout else ""
        eval_success = result.returncode == 0
    except subprocess.CalledProcessError as e:
        eval_out += f"{e.stderr.strip()}" if e.stderr else ""
        eval_out += f" |--| {e.stdout.strip()}" if e.stdout else ""

    # store results
    save_logs(results_dir_path, run_id, task_id, eval_success, agent_id, model_id, vague_descriptions, eval_out,
              exec_minutes, agent, log_interface, task_descr)

    return eval_success, exec_minutes, eval_out


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run agent - args parser")
    parser.add_argument("-i", "--run-id", required=True, help="Run id (int)", type=int)
    parser.add_argument("-t", "--task-id", required=True, help="Task id (int)", type=int)
    parser.add_argument("-g", "--agent-id", required=True, help="Agent id (str)", type=str)
    parser.add_argument("-m", "--model-id", required=True, help="Model id (str)", type=str)
    parser.add_argument("-a", "--agent-dir", required=True,
                        help="Path where to find the actual agentu repo (Path)", type=Path)
    parser.add_argument("-r", "--results-dir", required=True, help="Path where to store results to (Path)", type=Path)
    parser.add_argument("-o", "--home-dir", required=True, help="Home path of agent execution (Path)", type=Path)
    parser.add_argument("-v", "--vague-descriptions", default=False, action="store_true",
                        help="Run vague task descriptions")
    parser.add_argument("-f", "--feedback-iterations-max", required=True,
                        help="Max number of feedback iterations ('eval file outputs back to agent') (int)", type=int)
    args = parser.parse_args()

    # run task setup, agent and evaluation
    tasks_dir = args.agent_dir / "benchmark" / "ubuntu_bench" / "tasks"

    success, exec_minutes, eval_out = run_agent(args.task_id, args.run_id, args.agent_id, args.model_id,
                                                args.results_dir, args.agent_dir,
                                                tasks_dir, args.home_dir,
                                                args.feedback_iterations_max, args.vague_descriptions)

    log_out = f"-> done run: {args.run_id:02} - task: {args.task_id:02} - {exec_minutes:.1f}min"
    if success:
        questionary.print(f"{log_out} - success", style="fg:green")
    else:
        questionary.print(f"{log_out} - failure: {eval_out[:40]}", style="fg:orange")
