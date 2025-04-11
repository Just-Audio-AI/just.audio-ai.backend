from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = Field(
        validation_alias="DATABASE_URL",
        default="postgresql+asyncpg://postgres:password@0.0.0.0:5432/app_db",
    )
    WISPER_AI_BASE_URL: str = Field(
        validation_alias="WISPER_AI_BASE_URL",
        default="https://api.lemonfox.ai/v1/audio/transcriptions",
    )
    WISPER_AI_AUTH_TOKEN: str = Field(
        validation_alias="WISPER_AI_AUTH_TOKEN",
        default="x9YLlWxzSFQVMkmiYSzcur7T4Bf84zoT",
    )
    BASE_URL: str = Field(
        validation_alias="BASE_URL", default="https://9e26-46-226-166-83.ngrok-free.app"
    )

    @property
    def whisper_ai_callback_url(self) -> str:
        return f"{self.BASE_URL}/audio/convert/file/callback"


settings = Settings()
