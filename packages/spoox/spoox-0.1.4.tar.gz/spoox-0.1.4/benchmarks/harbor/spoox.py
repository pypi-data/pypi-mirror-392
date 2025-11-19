import os
import shlex
from pathlib import Path

from dotenv import load_dotenv
from harbor.agents.installed.base import BaseInstalledAgent
from harbor.models.agent.context import AgentContext
from pydantic import BaseModel


class ExecInput(BaseModel):
    command: str
    cwd: str | None = None
    env: dict[str, str] | None = None
    timeout_sec: int | None = None


_AGENT_ID = "mas-group-chat-m"  # "singleton",'mas-group-chat-s','mas-group-chat-m','mas-group-chat-l','mas-supervisor'
_AGENT_ID_CHAR = "m"
_MODEL_ID = "gpt-5-mini"  # "gpt-oss:20b","qwen3:14b","claude-sonnet-4-5","magistral:24b","gpt-5","gpt-5-mini"


class Spoox(BaseInstalledAgent):

    @staticmethod
    def name() -> str:
        return f"spoox-{_AGENT_ID_CHAR}"

    @property
    def _install_agent_template_path(self) -> Path:
        """
        Path to the jinja template script for installing the agent in the container.
        """
        return Path(__file__).parent / "install_spoox.sh"

    def create_run_agent_commands(self, instruction: str) -> list[ExecInput]:
        """
        Create the commands to run the agent in the container. Usually this is a single
        command that passes the instruction to the agent and executes it in headless
        mode.
        """
        # get chatgpt env
        load_dotenv()
        openai_api_key = str(os.environ.get("OPENAI_API_KEY"))
        safe_instruction = shlex.quote(instruction)
        cmd = f". /opt/venv/bin/activate && spoox -m {_MODEL_ID} -a {_AGENT_ID} -t {safe_instruction}"
        return [ExecInput(command=cmd, env={"OPENAI_API_KEY": openai_api_key})]

    def populate_context_post_run(self, context: AgentContext) -> None:
        """
        Populate the context with the results of the agent execution. Assumes the run()
        method has already been called. Typically, involves parsing a trajectory file.
        """
        # spoox creates own logs -> copied to harbor jobs folders separately
        pass
