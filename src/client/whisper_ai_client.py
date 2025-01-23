from dataclasses import dataclass
import httpx

CONVERTED_FORMAT_TO_RESPONSE_FORMAT = {}

@dataclass
class WhisperAIClient:
    base_url: str
    auth_token: str
    callback_url: str

    async def convert_audio_to_text(self, audio_file_url: str, response_format: str, language: str | None = None) -> str:
        data = {
            "file": audio_file_url,
            "response_format": CONVERTED_FORMAT_TO_RESPONSE_FORMAT[response_format],
            "callback_url": self.callback_url,
        }
        if language:
            data["language"] = language
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(url=f"{self.base_url}/v1/audio/transcriptions", headers={"Authorization": self.auth_token})
            return response.json()
