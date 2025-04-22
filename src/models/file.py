from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class UserFile(Base):
    __tablename__ = "user_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    file_url: Mapped[str]
    status: Mapped[str]
    external_id: Mapped[Optional[UUID]]
    display_name: Mapped[str]
    transcription: Mapped[Optional[dict]] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    duration: Mapped[Optional[int]] = mapped_column(
        comment="Длительность файла в секундах"
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        comment="Размер файла в байтах", nullable=True
    )
    mime_type: Mapped[Optional[str]] = mapped_column(
        comment="MIME-тип файла", nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationship with ChatSession
    chat_sessions = relationship("ChatSession", back_populates="user_file")
