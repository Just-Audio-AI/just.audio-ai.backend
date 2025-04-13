from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserFileBase(BaseModel):
    id: int
    user_id: int
    file_url: str
    status: str
    display_name: str
    external_id: UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserFileDetail(UserFileBase):
    transcription: dict | None = None
    duration: int | None = None

class UserFileListResponse(BaseModel):
    items: list[UserFileBase]

class UserFileListDetailResponse(BaseModel):
    items: list[UserFileDetail]

class FileTranscriptionRequest(BaseModel):
    file_ids: list[int]
