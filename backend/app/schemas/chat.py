from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # user | assistant | agent
    content: str
    agent_name: str | None = None


class ConversationHistory(BaseModel):
    conversation_id: str
    messages: list[ChatMessage]
