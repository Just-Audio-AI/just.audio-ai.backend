from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class ChatSenderType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_file_id: Mapped[int] = mapped_column(
        ForeignKey("user_files.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationship to UserFile (back-reference)
    user_file = relationship(
        "UserFile",
        back_populates="chat_sessions",
        foreign_keys=[user_file_id],
        primaryjoin="and_(ChatSession.user_file_id==UserFile.id, ChatSession.user_id==UserFile.user_id)",
    )

    # Relationship to messages
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="CASCADE")
    )
    sender: Mapped[str] = mapped_column(comment="Enum: 'user' or 'assistant'")
    content: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")
