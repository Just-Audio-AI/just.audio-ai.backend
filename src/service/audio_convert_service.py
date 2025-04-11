from dataclasses import dataclass

from src.client.whisper_ai_client import WhisperAIClient


@dataclass
class AudioConvertService:
    audio_ai_client: WhisperAIClient

    async def convert_audio_to_text(
        self,
        audio_file_url: str,
        response_format: str,
        callback_url: str,
        language: str | None,
    ) -> None:
        await self.audio_ai_client.convert_audio_to_text(
            audio_file_url, response_format, language, callback_url
        )
