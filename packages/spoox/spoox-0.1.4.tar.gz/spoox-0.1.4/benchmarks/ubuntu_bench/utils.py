import docker
from docker.models.containers import Container
from rich.table import Table

TASK_CONTAINER_NAME = "plaume/ubuntu-tasks:"
AGENTU_LOCAL_DIR_PATH = "/src"

CONTAINER_AGENTU_DIR = "/opt/agentu/src"
CONTAINER_AGENTU_RESULTS_PATH = "/opt/results"

CONTAINER_AGENT_RUNNABLE_PATH = f"{CONTAINER_AGENTU_DIR}/benchmark/ubuntu_bench/run_agent.py"
CONTAINER_AGENT_HOME_PATH = "/home/linus"

TASK_IDS = [i for i in range(1, 21)]
AVAILABLE_AGENT_IDS = ['singleton', 'mas-group-chat-s', 'mas-group-chat-m', 'mas-group-chat-l', 'mas-supervisor']
AVAILABLE_AGENT_MODELS = [
    'gpt-oss:20b-docker',  # no autogen ollama client _model_info
    'mistral-nemo:12b-docker',
    'magistral:24b-docker',  # no autogen ollama client _model_info
    'qwen3:8b-docker',
    'qwen3:14b-docker',
    'gpt-5-mini',  # no local model
    'claude-sonnet-4',  # no local model
]

_CLIENT = docker.from_env()


def setup_containers(run_id: int, task_ids: [int], results_dir_path: str, exec_id: str) -> [Container]:
    """Setup all docker containers for given task_ids."""

    # create all containers
    cs = []
    for task_id in task_ids:
        c = _CLIENT.containers.run(
            image=TASK_CONTAINER_NAME + str(task_id),
            name=f"ubuntu-bench-exec-{exec_id}-run-{run_id}-task-{task_id}",
            volumes={
                AGENTU_LOCAL_DIR_PATH: {
                    'bind': CONTAINER_AGENTU_DIR,
                    'mode': 'ro'
                },
                results_dir_path: {
                    'bind': CONTAINER_AGENTU_RESULTS_PATH,
                    'mode': 'rw'
                }
            },
            command="tail -f /dev/null",  # keeps the container running
            detach=True,
        )
        cs.append(c)

    # setup agentu in all containers
    for c in cs:
        exit_code, output = c.exec_run("pip install --no-cache-dir -r /opt/agentu/src/requirements.txt", user='linus')
        if exit_code != 0:
            raise RuntimeError(f"Setting up agentu on container failed with {exit_code}:\n"
                               f"output:\n{output.decode() if output is not None else ''}")
    return cs


def delete_containers(cs: [Container]) -> None:
    """Delete benchmark docker image and all containers"""
    for c in cs:
        c.remove()


def make_table(lines: list[str], n: int = 20):
    """Generates a 'rich' table of the last n lines."""
    # make sure a line has no line s itself
    all_lines = []
    for entry in lines:
        all_lines.extend(entry.splitlines())
    # split lines in lines
    table = Table(expand=True, show_header=False, style='#555555')
    for line in all_lines[-n:]:
        line_out = line[:80]
        line_out += "..." if len(line) > 80 else ""
        table.add_row(line_out, style='#555555')
    return table
