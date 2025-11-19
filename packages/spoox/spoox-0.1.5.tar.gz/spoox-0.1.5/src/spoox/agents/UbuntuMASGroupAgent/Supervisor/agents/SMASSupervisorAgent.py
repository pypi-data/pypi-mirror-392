import asyncio

from autogen_core.models import ChatCompletionClient

from spoox.agents.UbuntuMASGroupAgent.BaseGroupChatAgent import BaseGroupChatAgent
from spoox.agents.UbuntuMASGroupAgent.Supervisor.agents.utils import get_SMAS_SUPERVISOR_SYSTEM_MESSAGE
from spoox.environment.Environment import Environment
from spoox.environment.tools.CallAgentTool import CallAgentTool, set_publish_message_func
from spoox.interface.Interface import Interface


class SMASSupervisorAgent(BaseGroupChatAgent):

    def __init__(
            self,
            topic_type: str,
            group_chat_topic_type: str,
            environment: Environment,
            model_client: ChatCompletionClient,
            interface: Interface,
            usage_stats: dict,
            return_next_time_possible_event: asyncio.Event,
            finished_tag: str,
            available_agents: dict[str: str]
    ) -> None:

        # special: create a CallAgentTool and add it to the environment
        set_publish_message_func(topic_type, self.publish_message)
        environment.call_agent_tool = CallAgentTool(
            [finished_tag, *available_agents.keys()],
            topic_type,
            group_chat_topic_type
        )

        super().__init__(
            group_chat_topic_type=group_chat_topic_type,
            description="Responsible for supervising and guiding the task solution process, sequentially calling agents to solve the overall user task.",
            system_message=get_SMAS_SUPERVISOR_SYSTEM_MESSAGE(topic_type, finished_tag, available_agents),
            model_client=model_client,
            interface=interface,
            usage_stats=usage_stats,
            environment=environment,
            return_next_time_possible_event=return_next_time_possible_event,
            next_agent_topic_types=[finished_tag],
            max_internal_iterations=100
        )
