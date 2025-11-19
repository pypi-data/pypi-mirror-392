from anthropic import BaseModel
from autogen_core.models import UserMessage


class GroupChatMessage(BaseModel):
    nonce: str  # make sure each message is unique so handlers do not merge them if they are sent close together in time
    body: UserMessage


class RequestToSpeak(BaseModel):
    nonce: str  # make sure each message is unique so handlers do not merge them if they are sent close together in time
