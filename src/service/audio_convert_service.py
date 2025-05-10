from dataclasses import dataclass

from src.client.whisper_ai_client import WhisperAIClient
from src.models.enums import FileTranscriptionStatus
from src.service.user_file_service import UserFileService


@dataclass
class AudioConvertService:
    audio_ai_client: WhisperAIClient
    user_file_service: UserFileService

    async def convert_audio_to_text(
        self,
        file_id: int,
        audio_file_url: str,
        response_format: str,
        callback_url: str,
        language: str | None,
    ) -> None:
        try:
            await self.audio_ai_client.convert_audio_to_text(
                audio_file_url, response_format, language, callback_url
            )
        except:
            await self.user_file_service.update_files_transcription_status(
                file_ids=[file_id],
                status=FileTranscriptionStatus.FAILED
            )
