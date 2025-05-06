from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class UserFileBase(BaseModel):
    id: int
    user_id: int
    file_url: str
    status: str
    display_name: str
    external_id: UUID | None = None
    created_at: datetime
    file_size: int | None = None
    mime_type: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserFileDetail(UserFileBase):
    transcription: dict | None = None
    transcription_text: str | None = None
    transcription_vtt: str | None = None
    transcription_srt: str | None = None
    duration: int | None = None
    removed_noise_file_url: str | None = None
    removed_vocals_file_url: str | None = None
    removed_melody_file_url: str | None = None
    removed_noise_file_status: str | None = None
    removed_vocal_file_status: str | None = None
    removed_melody_file_status: str | None = None


class UserFileListResponse(BaseModel):
    items: list[UserFileBase]


class UserFileListDetailResponse(BaseModel):
    items: list[UserFileDetail]


class FileTranscriptionRequest(BaseModel):
    file_ids: list[int]


class TranscriptionUpdateRequest(BaseModel):
    transcription_type: str = Field(..., description="Type of transcription (json, text, vtt, srt)")
    data: str = Field(..., description="Transcription data as string")
