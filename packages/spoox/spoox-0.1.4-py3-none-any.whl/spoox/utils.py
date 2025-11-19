import json
import pickle
from pathlib import Path

from autogen_core.models import ChatCompletionClient
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient

from spoox.agents.AgentSystem import AgentSystem
from spoox.agents.UbuntuMASGroupAgent.StructuredFlow.AgentSystem_large import UbuntuMASGroupChatLarge
from spoox.agents.UbuntuMASGroupAgent.StructuredFlow.AgentSystem_medium import UbuntuMASGroupChatMedium
from spoox.agents.UbuntuMASGroupAgent.StructuredFlow.AgentSystem_small import UbuntuMASGroupChatSmall
from spoox.agents.UbuntuMASGroupAgent.Supervisor.AgentSystem_supervisor import UbuntuMASGroupChatSupervisor
from spoox.agents.UbuntuSingletonAgent.AgentSystem_singleton import UbuntuSingletonAgent
from spoox.environment.Environment import Environment
from spoox.interface import LogInterface
from spoox.interface.Interface import Interface


def setup_model_client(model_id: str, docker_access: bool = False) -> ChatCompletionClient:
    """
    Based on the provided 'model_id', create the corresponding model client instance.
    Field `docker_access` should be set to True if Ollama is called from the inside of a docker container.
    """

    if docker_access:
        host = "http://host.docker.internal:11434"
    else:
        host = "http://localhost:11434"

    if model_id in ["gpt-oss:20b", "gpt-oss:120b", "magistral:24b"]:
        model_info = {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
            "structured_output": True,
            "multiple_system_messages": False
        }
        return OllamaChatCompletionClient(model=model_id, model_info=model_info, host=host)

    if model_id in ["qwen3:8b", "qwen3:14b", "mistral-nemo:12b"]:
        return OllamaChatCompletionClient(model=model_id, host=host)
    if model_id == "claude-sonnet-4":
        return AnthropicChatCompletionClient(model="claude-sonnet-4-20250514")
    if model_id == "claude-sonnet-4-5":
        return AnthropicChatCompletionClient(model="claude-sonnet-4-5-20250929")
    if model_id in ["gpt-5", "gpt-5-mini"]:
        return OpenAIChatCompletionClient(model=model_id)

    raise ValueError(f"Selected model '{model_id}' not known.")


def setup_agent_system(agent_id: str, model_client: ChatCompletionClient,
                       environment: Environment, interface: Interface, timeout: int = 3600) -> AgentSystem:
    """Based on the provided 'agent_id', create the corresponding agent system instance."""

    if agent_id == "singleton":
        return UbuntuSingletonAgent(interface, model_client, environment, timeout)
    if agent_id == "mas-group-chat-s":
        return UbuntuMASGroupChatSmall(interface, model_client, environment, timeout)
    if agent_id == "mas-group-chat-m":
        return UbuntuMASGroupChatMedium(interface, model_client, environment, timeout)
    if agent_id == "mas-group-chat-l":
        return UbuntuMASGroupChatLarge(interface, model_client, environment, timeout)
    if agent_id == "mas-supervisor":
        return UbuntuMASGroupChatSupervisor(interface, model_client, environment, timeout)
    raise ValueError(f"Selected agent '{agent_id}' not known.")


def save_logs(results_dir_path: Path, run_id: int, task_id: str, success: bool, agent_id: str, model_id: str,
              vague_description: bool, eval_out: str, exec_minutes: float, agent: AgentSystem,
              log_interface: LogInterface, task_instruction: str) -> None:
    """Store task execution results in uniform format."""

    # save the execution meta-data as a json file
    with (results_dir_path / f"run_{run_id}_task_{task_id}_exec_meta_data.json").open("w") as f:
        exec_meta_data = {
            "task": task_id,
            "success": success,
            "agent": agent_id,
            "model": model_id,
            "vague_description": vague_description,
            "eval_out": eval_out,
            "feedback_iterations_done": log_interface.feedback_iterations_done,
            "exec_time": exec_minutes,
            "task_instruction": task_instruction
        }
        json.dump(exec_meta_data, f, indent=4)
    # save the agent_usage_stats dict in a pickle file
    with (results_dir_path / f"run_{run_id}_task_{task_id}_agent_usage_stats.pkl").open("wb") as f:
        pickle.dump(agent.usage_stats, f)
    # save the agent system state as a dict in a pickle file
    with (results_dir_path / f"run_{run_id}_task_{task_id}_agent_system_state.pkl").open("wb") as f:
        pickle.dump(agent.get_state(), f)
    # save the interface logs in a pickle file
    with (results_dir_path / f"run_{run_id}_task_{task_id}_log_interface.pkl").open("wb") as f:
        pickle.dump(log_interface, f)
