from anthropic import BaseModel
from autogen_core.models import UserMessage


class PublicMessage(BaseModel):
    body: UserMessage
