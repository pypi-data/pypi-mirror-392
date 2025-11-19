from abc import abstractmethod, ABC

from autogen_core.models import ChatCompletionClient

from spoox.environment.Environment import Environment
from spoox.interface.Interface import Interface


class AgentSystem(ABC):

    def __init__(self, interface: Interface, model_client: ChatCompletionClient,
                 environment: Environment, timeout: int = 3600):
        self.interface = interface
        self.model_client = model_client
        self.environment = environment
        self.timeout = timeout
        self.usage_stats = dict()
        self.init_usage_stats()

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    def init_usage_stats(self):
        pass

    @abstractmethod
    def get_state(self):
        pass
