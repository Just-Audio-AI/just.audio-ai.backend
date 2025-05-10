from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        validation_alias="DATABASE_URL",
        default="postgresql+asyncpg://postgres:password@db:5432/app_db",
    )
    WISPER_AI_BASE_URL: str = Field(
        validation_alias="WISPER_AI_BASE_URL",
        default="https://api.lemonfox.ai/v1/audio/transcriptions",
    )
    WISPER_AI_AUTH_TOKEN: str = Field(
        validation_alias="WISPER_AI_AUTH_TOKEN",
        default="x9YLlWxzSFQVMkmiYSzcur7T4Bf84zoT",
    )
    PROXY_URL: str = Field(
        validation_alias="PROXY_URL",
        default="url"
    )
    BASE_URL: str = Field(
        validation_alias="BASE_URL",
        default="https://c928-46-226-166-83.ngrok-free.app",
    )
    from_email: str = "just.audio.ai@saidmagomedov.ru"
    SMTP_PORT: int = 465
    SMTP_HOST: str = "smtp.yandex.ru"
    SMTP_PASSWORD: str = "tkorlhjwddkalbqy"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 100000
    token_secret: str = "Sdasdad3w#RmF34ef43%E5&*6DV%$5DSvBF*fY9V(y*&VNFdfBU(t8DnfDS"
    token_algorithm: str = "HS256"

    # OpenAI settings
    OPENAI_API_KEY: str = Field(
        validation_alias="OPENAI_API_KEY",
        default="sk-your-api-key",
    )
    OPENAI_MODEL: str = Field(
        validation_alias="OPENAI_MODEL",
        default="gpt-3.5-turbo",
    )

    @property
    def whisper_ai_callback_url(self) -> str:
        return f"{self.BASE_URL}/audio/convert/file/callback"

    class Config:
        env_file = ".env"


settings = Settings()
