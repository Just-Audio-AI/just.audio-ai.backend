from dataclasses import dataclass

import httpx


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

        async with httpx.AsyncClient(timeout=None) as client:
            try:
                response = await client.post(
                    url=f"{self.base_url}",
                    json=data,
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                )
                response.raise_for_status()
                return response.json()
            except httpx.ReadTimeout:
                pass
