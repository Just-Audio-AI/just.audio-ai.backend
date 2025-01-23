from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import mapped_column, Mapped

from src.models import Base


class UserFile(Base):
    __tablename__ = 'user_files'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    file_url: Mapped[str]
    status: Mapped[str]
    external_id: Mapped[Optional[UUID]]
    display_name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
