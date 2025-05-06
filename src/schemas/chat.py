from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ChatMessageBase(BaseModel):
    sender: str
    content: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class GPTModelType(Enum):
    PRO = "pro"
    HIGH_SPEED = "high-speed"
    THINKING = "thinking"


class ChatMessageCreate(BaseModel):
    message: str
    model: GPTModelType


GPT_MODEL_NAME_TO_OPENAI_MODEL = {
    GPTModelType.PRO: "gpt-4o",
    GPTModelType.HIGH_SPEED: "gpt-4o-mini",
    GPTModelType.THINKING: "o4-mini"
}


class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: int


class ChatSessionBase(BaseModel):
    user_file_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionResponse(ChatSessionBase):
    id: int
    messages: list[ChatMessageResponse] = []


class ChatResponse(BaseModel):
    message: str
    error: bool = False
    limit_exceeded: bool = False
