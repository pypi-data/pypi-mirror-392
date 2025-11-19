import asyncio

from autogen_core import SingleThreadedAgentRuntime, DefaultTopicId
from autogen_core import TypeSubscription
from autogen_core.models import UserMessage, ChatCompletionClient

from spoox.agents.AgentSystem import AgentSystem
from spoox.agents.UbuntuSingletonAgent.Message import PublicMessage
from spoox.agents.UbuntuSingletonAgent.SingletonAgent import SingletonAgent
from spoox.environment.Environment import Environment
from spoox.interface.Interface import Interface


class UbuntuSingletonAgent(AgentSystem):

    assistant_topic_type = "assistant"

    def __init__(self, interface: Interface, model_client: ChatCompletionClient,
                 environment: Environment, timeout: int = 3600):

        super().__init__(interface, model_client, environment, timeout)

        self.runtime = SingleThreadedAgentRuntime()

        # create timeout event to tell agents to return next the time possible
        self._timeout_event = None

        # agents
        self._singleton_agent = None

    async def build_agent(self):
        """setup all agents"""

        self._singleton_agent = await SingletonAgent.register(
            self.runtime,
            self.assistant_topic_type,
            lambda: SingletonAgent(
                description="Assistant that that solves server and command-line related tasks",
                environment=self.environment,
                model_client=self.model_client,
                interface=self.interface,
                usage_stats=self.usage_stats,
                return_next_time_possible_event=self._timeout_event,
            ),
        )
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.assistant_topic_type, agent_type=self._singleton_agent.type))

    async def start(self):

        if self._timeout_event is None:
            self._timeout_event = asyncio.Event()
        await self.environment.start()
        await self.build_agent()

        # user input loop
        while True:

            user_input = self.interface.request_user_input("Query...")
            self.usage_stats['user_interactions_count'] += 1

            # exit
            if user_input in ['q', 'exit', 'stop']:
                break

            # reset stop signal
            if self._timeout_event.is_set():
                self._timeout_event.clear()

            # send user input to the singleton agent
            self.runtime.start()
            await self.runtime.publish_message(
                message=PublicMessage(body=UserMessage(content=user_input, source="User")),
                topic_id=DefaultTopicId(type=self.assistant_topic_type),
            )

            # wait until the agents are complete (runtime is idle)
            # if we just stop the runtime, but agents are still working on it -> autogen runtime will raise ValueError
            # therefore we use an event to signal all agent to stop the next time possible
            async def _timeout():
                await asyncio.sleep(self.timeout)
                error_message = "Agent System waiting for runtime.stop_when_idle timeout error"
                print(error_message)  # todo to be deleted
                self.interface.print_highlight(error_message, "TimeoutError")
                self.usage_stats["agent_errors"].append(("TimeoutError", error_message))
                self._timeout_event.set()
            timeout_task = asyncio.create_task(_timeout())
            await self.runtime.stop_when_idle()
            timeout_task.cancel()

        # stop entirely
        await self.environment.stop()
        await self.runtime.close()

    def init_usage_stats(self):
        self.usage_stats['user_interactions_count'] = 0
        self.usage_stats['llm_calls_count'] = 0
        self.usage_stats['tool_call_counts'] = dict()
        self.usage_stats['tool_calls'] = []
        self.usage_stats['ollama_response_error_count'] = 0
        self.usage_stats['model_client_exceptions'] = []
        self.usage_stats['agent_errors'] = []
        self.usage_stats['prompt_tokens'] = []
        self.usage_stats['completion_tokens'] = []

    def get_state(self):
        return {
            'single_agent_type': self._singleton_agent
        }
