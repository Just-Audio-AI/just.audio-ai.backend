import logging
from dataclasses import dataclass

import httpx

from src.settings import settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class WhisperAIClient:
    base_url: str
    auth_token: str

    async def convert_audio_to_text(
        self,
        audio_file_url: str,
        response_format: str,
        language: str | None = None,
        callback_url: str | None = None,
    ) -> str:
        data = {
            "file": audio_file_url,
            "response_format": response_format,
            "callback_url": callback_url,
        }
        if language:
            data["language"] = language

        async with httpx.AsyncClient(timeout=None, proxy=settings.PROXY_URL) as client:
            try:
                response = await client.post(
                    url=f"{self.base_url}",
                    json=data,
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                )
                logger.info(f"Запрос в whisper  по audio_file_url{audio_file_url}")
                return response.json()
            except httpx.ReadTimeout:
                pass
