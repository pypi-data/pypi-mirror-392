import asyncio
import uuid

from autogen_core import SingleThreadedAgentRuntime, DefaultTopicId
from autogen_core import TypeSubscription
from autogen_core.models import UserMessage, ChatCompletionClient

from spoox.agents.AgentSystem import AgentSystem
from spoox.agents.UbuntuMASGroupAgent.Message import GroupChatMessage, RequestToSpeak
from spoox.agents.UbuntuMASGroupAgent.Supervisor.agents.SMASApproverAgent import SMASApproverAgent
from spoox.agents.UbuntuMASGroupAgent.Supervisor.agents.SMASStopperAgent import SMASStopperAgent
from spoox.agents.UbuntuMASGroupAgent.Supervisor.agents.SMASSummarizerAgent import SMASSummarizerAgent
from spoox.agents.UbuntuMASGroupAgent.Supervisor.agents.SMASSupervisorAgent import SMASSupervisorAgent

from spoox.agents.UbuntuMASGroupAgent.Supervisor.agents.SMASTesterAgent import SMASTesterAgent
from spoox.agents.UbuntuMASGroupAgent.Supervisor.agents.SMASExplorerAgent import SMASExplorerAgent
from spoox.agents.UbuntuMASGroupAgent.Supervisor.agents.SMASPlanExecutorAgent import SMASPlanExecutorAgent
from spoox.agents.UbuntuMASGroupAgent.Supervisor.agents.utils import SMAS_AGENT_TAGS_AND_DESCRIPTIONS
from spoox.environment.Environment import Environment
from spoox.interface.Interface import Interface


class UbuntuMASGroupChatSupervisor(AgentSystem):

    # all topic types
    group_chat_topic_type = "group-chat"
    supervisor_topic_type = "supervisor"
    explorer_topic_type = "explorer"
    solver_topic_type = "solver"
    tester_topic_type = "tester"
    approver_topic_type = "approver"
    summarizer_topic_type = "summarizer"
    finished_topic_type = "finished"

    def __init__(self, interface: Interface, model_client: ChatCompletionClient,
                 environment: Environment, timeout: int = 3600):

        super().__init__(interface, model_client, environment, timeout)

        self.runtime = SingleThreadedAgentRuntime()

        # create timeout event to tell agents to return next the time possible
        self._timeout_event = None

        # agents
        self._supervisor_agent = None
        self._explorer_agent = None
        self._solver_agent = None
        self._tester_agent = None
        self._approver_agent = None
        self._summarizer_agent = None
        self._stopper_agent = None

    async def build_mas(self):
        """setup all agents"""

        self._supervisor_agent = await SMASSupervisorAgent.register(
            self.runtime,
            self.supervisor_topic_type,
            lambda: SMASSupervisorAgent(
                topic_type=self.supervisor_topic_type,
                group_chat_topic_type=self.group_chat_topic_type,
                environment=self.environment,
                model_client=self.model_client,
                interface=self.interface,
                usage_stats=self.usage_stats,
                return_next_time_possible_event=self._timeout_event,
                finished_tag=self.finished_topic_type,
                available_agents=SMAS_AGENT_TAGS_AND_DESCRIPTIONS,
            ),
        )
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.supervisor_topic_type, agent_type=self._supervisor_agent.type))
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.group_chat_topic_type, agent_type=self._supervisor_agent.type))

        self._explorer_agent = await SMASExplorerAgent.register(
            self.runtime,
            self.explorer_topic_type,
            lambda: SMASExplorerAgent(
                topic_type=self.explorer_topic_type,
                group_chat_topic_type=self.group_chat_topic_type,
                environment=self.environment,
                model_client=self.model_client,
                interface=self.interface,
                usage_stats=self.usage_stats,
                return_next_time_possible_event=self._timeout_event,
                supervisor_agent_topic_type=self.supervisor_topic_type,
            ),
        )
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.explorer_topic_type, agent_type=self._explorer_agent.type))
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.group_chat_topic_type, agent_type=self._explorer_agent.type))

        self._solver_agent = await SMASPlanExecutorAgent.register(
            self.runtime,
            self.solver_topic_type,
            lambda: SMASPlanExecutorAgent(
                topic_type=self.solver_topic_type,
                group_chat_topic_type=self.group_chat_topic_type,
                environment=self.environment,
                model_client=self.model_client,
                interface=self.interface,
                usage_stats=self.usage_stats,
                return_next_time_possible_event=self._timeout_event,
                supervisor_agent_topic_type=self.supervisor_topic_type,
            ),
        )
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.solver_topic_type, agent_type=self._solver_agent.type))
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.group_chat_topic_type, agent_type=self._solver_agent.type))

        self._tester_agent = await SMASTesterAgent.register(
            self.runtime,
            self.tester_topic_type,
            lambda: SMASTesterAgent(
                topic_type=self.tester_topic_type,
                group_chat_topic_type=self.group_chat_topic_type,
                environment=self.environment,
                model_client=self.model_client,
                interface=self.interface,
                usage_stats=self.usage_stats,
                return_next_time_possible_event=self._timeout_event,
                supervisor_agent_topic_type=self.supervisor_topic_type,
            ),
        )
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.tester_topic_type, agent_type=self._tester_agent.type))
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.group_chat_topic_type, agent_type=self._tester_agent.type))

        self._approver_agent = await SMASApproverAgent.register(
            self.runtime,
            self.approver_topic_type,
            lambda: SMASApproverAgent(
                topic_type=self.approver_topic_type,
                group_chat_topic_type=self.group_chat_topic_type,
                environment=self.environment,
                model_client=self.model_client,
                interface=self.interface,
                usage_stats=self.usage_stats,
                return_next_time_possible_event=self._timeout_event,
                supervisor_agent_topic_type=self.supervisor_topic_type,
            ),
        )
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.approver_topic_type, agent_type=self._approver_agent.type))
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.group_chat_topic_type, agent_type=self._approver_agent.type))

        self._summarizer_agent = await SMASSummarizerAgent.register(
            self.runtime,
            self.summarizer_topic_type,
            lambda: SMASSummarizerAgent(
                topic_type=self.summarizer_topic_type,
                group_chat_topic_type=self.group_chat_topic_type,
                environment=self.environment,
                model_client=self.model_client,
                interface=self.interface,
                usage_stats=self.usage_stats,
                return_next_time_possible_event=self._timeout_event,
                supervisor_agent_topic_type=self.supervisor_topic_type,
            ),
        )
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.summarizer_topic_type, agent_type=self._summarizer_agent.type))
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.group_chat_topic_type, agent_type=self._summarizer_agent.type))

        self._stopper_agent = await SMASStopperAgent.register(
            self.runtime,
            self.finished_topic_type,
            lambda: SMASStopperAgent(),
        )
        await self.runtime.add_subscription(
            TypeSubscription(topic_type=self.finished_topic_type, agent_type=self._stopper_agent.type))

    async def start(self):

        if self._timeout_event is None:
            self._timeout_event = asyncio.Event()
        await self.environment.start()
        await self.build_mas()

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

            # send user input to the group chat and trigger explorer agent
            self.runtime.start()
            await self.runtime.publish_message(
                message=GroupChatMessage(nonce=str(uuid.uuid4()), body=UserMessage(content=user_input, source="User")),
                topic_id=DefaultTopicId(type=self.group_chat_topic_type)
            )
            await asyncio.sleep(0.1)  # ensuring the group msg can be observed before the RTS (I think it is not required - but not sure...)
            await self.runtime.publish_message(
                message=RequestToSpeak(nonce=str(uuid.uuid4())),
                topic_id=DefaultTopicId(type=self.supervisor_topic_type)
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
        self.usage_stats['supervisor_agent_calling_chain'] = []
        self.usage_stats['next_agent_calling_chain'] = []
        self.usage_stats['group_chat_message_lengths'] = []

    def get_state(self):
        return {
            'supervisor_agent': self._supervisor_agent,
            'explorer_agent': self._explorer_agent,
            'solver_agent': self._solver_agent,
            'tester_agent': self._tester_agent,
            'approver_agent': self._approver_agent,
            'summarizer_agent': self._summarizer_agent,
            'stopper_agent': self._stopper_agent,
        }
