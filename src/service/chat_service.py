from dataclasses import dataclass
from typing import Dict, Optional, Tuple


from src.client.openai_client import OpenAIClient
from src.models.chat import ChatMessage, ChatSession, ChatSenderType
from src.models.file import UserFile
from src.repository.chat_repository import ChatRepository
from src.repository.products_repository import ProductsRepository
from src.repository.user_products_repository import UserProductsRepository


@dataclass
class ChatService:
    chat_repository: ChatRepository
    openai_client: OpenAIClient
    user_products_repository: UserProductsRepository
    product_repository: ProductsRepository

    async def get_or_create_chat_session(self, user_file_id: int) -> ChatSession:
        """Get an existing chat session or create a new one if none exists."""
        session = await self.chat_repository.get_chat_session(user_file_id)
        if not session:
            session = await self.chat_repository.create_chat_session(user_file_id)
        return session

    async def save_user_message(self, session_id: int, content: str) -> ChatMessage:
        """Save a user message to the database."""
        return await self.chat_repository.create_chat_message(
            session_id=session_id, sender=ChatSenderType.USER.value, content=content
        )

    async def save_assistant_message(
        self, session_id: int, content: str
    ) -> ChatMessage:
        """Save an assistant message to the database."""
        return await self.chat_repository.create_chat_message(
            session_id=session_id,
            sender=ChatSenderType.ASSISTANT.value,
            content=content,
        )

    async def get_user_file(self, file_id: int) -> Optional[UserFile]:
        """Get a user file by ID."""
        return await self.chat_repository.get_user_file(file_id)

    async def check_gpt_limits(
        self, user_id: int, file_id: int
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Проверяет, не превышены ли лимиты GPT-запросов для пользователя.

        Args:
            user_id: ID пользователя
            file_id: ID файла, для которого делается запрос

        Returns:
            Tuple из (can_use_gpt, message, session_id):
            - can_use_gpt: True если пользователь может использовать GPT, False в противном случае
            - message: Сообщение с причиной, если GPT недоступен
            - session_id: ID сессии чата, если существует
        """
        # Получаем активную подписку пользователя
        active_product = await self.user_products_repository.get_user_subscriptions(
            user_id, is_active=True
        )

        if not active_product:
            return (
                False,
                "У вас нет активной подписки для использования GPT-ассистента",
                None,
            )

        # Получаем информацию о продукте
        product_info = await self.product_repository.get_by_id(
            active_product[0].product_id
        )

        if not product_info:
            return False, "Не удалось найти информацию о вашей подписке", None

        # Проверяем, включен ли GPT в подписку
        if product_info.gpt_request_limit_one_file is None:
            return False, "GPT-ассистент не включен в вашу подписку", None

        # Если лимит равен 0, значит неограниченное количество запросов
        if product_info.gpt_request_limit_one_file == 0:
            # Получаем ID сессии, если она существует
            message_count, session_id = (
                await self.chat_repository.get_user_message_count(file_id)
            )
            return True, "", session_id

        # Получаем количество сообщений и ID сессии одним запросом
        message_count, session_id = await self.chat_repository.get_user_message_count(
            file_id
        )

        if message_count >= product_info.gpt_request_limit_one_file:
            return (
                False,
                f"Вы достигли лимита запросов ({product_info.gpt_request_limit_one_file}) к GPT-ассистенту для этого файла",
                session_id,
            )

        return True, "", session_id

    async def process_message(
        self, file_id: int, message_content: str, user_id: int
    ) -> Dict:
        """Process a user message, get an assistant response, and save both to the database."""
        # Get user file
        user_file = await self.get_user_file(file_id)
        if not user_file:
            raise ValueError(f"User file with ID {file_id} not found.")

        # Проверяем лимиты GPT и получаем ID существующей сессии, если она есть
        can_use_gpt, limit_message, existing_session_id = await self.check_gpt_limits(
            user_id, file_id
        )
        if not can_use_gpt:
            return {"message": limit_message, "error": True, "limit_exceeded": True}

        # Получаем или создаем сессию чата
        session = None
        if existing_session_id:
            # Используем существующую сессию или создаем новую, если потребуется
            # Начало - получаем саму сессию целиком, а не только ID
            session = await self.get_or_create_chat_session(file_id)
        else:
            # Создаем новую сессию, так как существующей нет
            session = await self.chat_repository.create_chat_session(file_id)

        # Save user message
        await self.save_user_message(session.id, message_content)

        # Create context with transcription if available
        system_message = "You are a helpful assistant analyzing audio files. "
        if user_file.transcription:
            transcription_text = self._extract_transcription_text(
                user_file.transcription
            )
            system_message += (
                f"Here is the transcription of the audio file: {transcription_text}"
            )

        # Get previous messages
        previous_messages = await self.chat_repository.get_chat_messages(session.id)

        # Format messages for OpenAI
        openai_messages = [{"role": "system", "content": system_message}]

        # Add previous messages (limit to last 10 for context)
        for prev_msg in previous_messages[-10:]:
            role = (
                "user" if prev_msg.sender == ChatSenderType.USER.value else "assistant"
            )
            openai_messages.append({"role": role, "content": prev_msg.content})

        # Get response from OpenAI
        assistant_response = await self.openai_client.get_chat_response(openai_messages)

        # Save assistant response
        await self.save_assistant_message(session.id, assistant_response)

        return {"message": assistant_response, "error": False, "limit_exceeded": False}

    async def get_chat_history(self, file_id: int) -> Optional[ChatSession]:
        """Get chat history for a file, including all messages."""
        # Get user file
        user_file = await self.get_user_file(file_id)
        if not user_file:
            raise ValueError(f"User file with ID {file_id} not found.")

        # Get or create chat session
        session = await self.get_or_create_chat_session(file_id)

        # Make sure we fetch all messages
        session.messages = await self.chat_repository.get_chat_messages(session.id)

        return session

    def _extract_transcription_text(self, transcription: dict) -> str:
        """Extract text from transcription object."""
        if not transcription:
            return ""

        # If the transcription has segments, extract text from them
        if "segments" in transcription:
            return " ".join(
                [segment.get("text", "") for segment in transcription["segments"]]
            )

        # If there's a text field, use that
        if "text" in transcription:
            return transcription["text"]

        # Otherwise, convert the whole thing to a string
        return str(transcription)
