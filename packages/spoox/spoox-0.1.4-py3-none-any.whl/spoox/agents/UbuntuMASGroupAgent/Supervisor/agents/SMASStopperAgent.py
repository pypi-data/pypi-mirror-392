from autogen_core import RoutedAgent, message_handler, MessageContext

from spoox.agents.UbuntuMASGroupAgent.Message import RequestToSpeak


class SMASStopperAgent(RoutedAgent):

    def __init__(self) -> None:
        super().__init__(description="The agent just stops the MAS flow and returns without taking any action.")

    @message_handler
    async def handle_request_to_speak(self, message: RequestToSpeak, ctx: MessageContext) -> None:
        # intentionally do nothing -> will stop runtime (see runtime.stop_when_idle in agent system)
        pass
