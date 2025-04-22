from dataclasses import dataclass

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.chat import ChatMessage, ChatSession, ChatSenderType
from src.models.file import UserFile


@dataclass
class ChatRepository:
    db: AsyncSession

    async def create_chat_session(self, user_file_id: int) -> ChatSession:
        """Create a new chat session for a user file."""
        # Сначала получаем user_file, чтобы узнать user_id
        user_file = await self.get_user_file(user_file_id)
        if not user_file:
            raise ValueError(f"User file with ID {user_file_id} not found")

        # Создаем новую сессию с правильным user_file_id и user_id
        session = ChatSession(user_file_id=user_file_id, user_id=user_file.user_id)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_chat_session(self, user_file_id: int) -> ChatSession | None:
        """Get a chat session by user file ID or return None if it doesn't exist."""
        # Сначала получаем user_file, чтобы узнать user_id
        user_file = await self.get_user_file(user_file_id)
        if not user_file:
            return None

        result = await self.db.execute(
            select(ChatSession)
            .where(
                (ChatSession.user_file_id == user_file_id)
                & (ChatSession.user_id == user_file.user_id)
            )
            .options(selectinload(ChatSession.messages))
            .order_by(ChatSession.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def get_user_message_count(self, user_file_id: int) -> tuple[int, int | None]:
        """
        Подсчитывает количество сообщений пользователя для указанного файла
        и возвращает ID сессии, если она существует.

        Returns:
            Tuple[int, Optional[int]]: (количество сообщений, id сессии)
            Если сессия не найдена, возвращается (0, None)
        """
        # Получаем user_file для определения user_id
        user_file = await self.get_user_file(user_file_id)
        if not user_file:
            return 0, None

        # Подзапрос для получения ID сессии
        session_subquery = (
            select(ChatSession.id)
            .where(
                (ChatSession.user_file_id == user_file_id)
                & (ChatSession.user_id == user_file.user_id)
            )
            .scalar_subquery()
        )

        # Основной запрос для подсчета сообщений пользователя
        result = await self.db.execute(
            select(
                func.count(ChatMessage.id).label("message_count"),
                session_subquery.label("session_id"),
            )
            .select_from(ChatMessage)
            .where(
                (ChatMessage.session_id == session_subquery)
                & (ChatMessage.sender == ChatSenderType.USER.value)
            )
        )

        row = result.one_or_none()
        if row:
            return row.message_count, row.session_id

        # Запрос для получения ID сессии (если сессия существует, но нет сообщений)
        session_result = await self.db.execute(
            select(ChatSession.id).where(
                (ChatSession.user_file_id == user_file_id)
                & (ChatSession.user_id == user_file.user_id)
            )
        )

        session_id = session_result.scalar_one_or_none()
        return 0, session_id

    async def create_chat_message(
        self, session_id: int, sender: str, content: str
    ) -> ChatMessage:
        """Add a new message to a chat session."""
        message = ChatMessage(session_id=session_id, sender=sender, content=content)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_chat_messages(self, session_id: int) -> list[ChatMessage]:
        """Get all messages for a chat session ordered by timestamp."""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp)
        )
        return result.scalars().all()

    async def get_user_file(self, file_id: int) -> UserFile | None:
        """Get a user file by ID."""
        result = await self.db.execute(select(UserFile).where(UserFile.id == file_id))
        return result.scalar_one_or_none()
