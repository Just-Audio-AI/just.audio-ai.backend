from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.enums import FileRemoveNoiseStatus, FileRemoveVocalStatus, FileRemoveMelodyStatus, \
    FileImproveAudioStatus, FileTranscriptionStatus


class UserFile(Base):
    __tablename__ = "user_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    file_url: Mapped[str]
    status: Mapped[str]
    external_id: Mapped[Optional[UUID]]
    display_name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_onupdate=func.now(), server_default=func.now())
    transcription_status: Mapped[Optional[str]] = mapped_column(
        comment="Статус расшифровки", default=FileTranscriptionStatus.NOT_STARTED.value
    )
    transcription: Mapped[Optional[dict]] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    # Transcription formatted outputs
    transcription_text: Mapped[Optional[str]] = mapped_column(
        comment="Транскрипция в формате plain text", nullable=True
    )
    transcription_vtt: Mapped[Optional[str]] = mapped_column(
        comment="Транскрипция в формате VTT", nullable=True
    )
    transcription_srt: Mapped[Optional[str]] = mapped_column(
        comment="Транскрипция в формате SRT", nullable=True
    )
    duration: Mapped[Optional[float]] = mapped_column(
        comment="Длительность файла в секундах"
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        comment="Размер файла в байтах", nullable=True
    )
    mime_type: Mapped[Optional[str]] = mapped_column(
        comment="MIME-тип файла", nullable=True
    )
    removed_noise_file_url: Mapped[Optional[str]] = mapped_column(
        comment="Ссылка на файл с удаленным шумом", nullable=True
    )
    removed_noise_file_status: Mapped[Optional[str]] = mapped_column(
        comment="Статус удаления шума", default=FileRemoveNoiseStatus.NOT_STARTED.value
    )
    removed_vocals_file_url: Mapped[Optional[str]] = mapped_column(
        comment="Ссылка на файл с удаленным вокалом", nullable=True
    )
    removed_vocal_file_status: Mapped[Optional[str]] = mapped_column(
        comment="Статус удаления голоса", default=FileRemoveVocalStatus.NOT_STARTED.value
    )
    removed_melody_file_url: Mapped[Optional[str]] = mapped_column(
        comment="Ссылка на файл с удаленной мелодией", nullable=True
    )
    removed_melody_file_status: Mapped[Optional[str]] = mapped_column(
        comment="Статус удаления голоса", default=FileRemoveMelodyStatus.NOT_STARTED.value
    )
    improved_audio_file_url: Mapped[Optional[str]] = mapped_column(
        comment="Ссылка на файл с улучшенным аудио", nullable=True
    )
    improved_audio_file_status: Mapped[Optional[str]] = mapped_column(
        comment="Статус улучшения аудио", default=FileImproveAudioStatus.NOT_STARTED.value
    )

    # Relationship with ChatSession
    chat_sessions = relationship("ChatSession", back_populates="user_file")
