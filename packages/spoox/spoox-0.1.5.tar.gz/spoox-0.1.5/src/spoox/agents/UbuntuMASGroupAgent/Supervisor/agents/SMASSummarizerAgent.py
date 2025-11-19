import asyncio

from autogen_core.models import ChatCompletionClient

from spoox.agents.UbuntuMASGroupAgent.BaseGroupChatAgent import BaseGroupChatAgent
from spoox.agents.UbuntuMASGroupAgent.Supervisor.agents.utils import get_SMAS_SUMMARIZER_SYSTEM_MESSAGE
from spoox.environment.Environment import Environment
from spoox.interface.Interface import Interface


class SMASSummarizerAgent(BaseGroupChatAgent):

    def __init__(
            self,
            topic_type: str,
            group_chat_topic_type: str,
            environment: Environment,
            model_client: ChatCompletionClient,
            interface: Interface,
            usage_stats: dict,
            return_next_time_possible_event: asyncio.Event,
            supervisor_agent_topic_type: str,
    ) -> None:
        super().__init__(
            group_chat_topic_type=group_chat_topic_type,
            description="Specialized evaluating and deciding if the agents have done enough work on the task, "
                        "checking their understanding, solutions, and testing, using all information and steps from previous agents.",
            system_message=get_SMAS_SUMMARIZER_SYSTEM_MESSAGE(topic_type, supervisor_agent_topic_type),
            model_client=model_client,
            interface=interface,
            usage_stats=usage_stats,
            environment=environment,
            return_next_time_possible_event=return_next_time_possible_event,
            next_agent_topic_types=[supervisor_agent_topic_type],
            max_internal_iterations=10,
        )
