from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatMessageBase(BaseModel):
    sender: str
    content: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageCreate(BaseModel):
    message: str


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
