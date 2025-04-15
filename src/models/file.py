from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

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
    duration: Mapped[Optional[int]] = mapped_column(comment="Длительность файла в секундах")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
