from pydantic import Field
from pydantic_settings import BaseSettings


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
        validation_alias="BASE_URL", default="https://f001-2a0b-4140-5070-00-2.ngrok-free.app"
    )
    S3_URL: str = Field(
        validation_alias="S3_URL", default="https://57fc-46-226-166-83.ngrok-free.app"
    )
    from_email: str = "i@saidmagomedov.ru"
    SMTP_PORT: int = 465
    SMTP_HOST: str = "smtp.yandex.ru"
    SMTP_PASSWORD: str = "tkorlhjwddkalbqy"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 100000
    token_secret: str = "Sdasdad3w#RmF34ef43%E5&*6DV%$5DSvBF*fY9V(y*&VNFdfBU(t8DnfDS"
    token_algorithm: str = "HS256"

    # CloudPayments settings
    cloudpayments_public_id: str = Field(validation_alias="CLOUDPAYMENTS_PUBLIC_ID")
    cloudpayments_api_secret: str = Field(validation_alias="CLOUDPAYMENTS_API_SECRET")

    @property
    def whisper_ai_callback_url(self) -> str:
        return f"{self.BASE_URL}/audio/convert/file/callback"

    class Config:
        env_file = ".env"


settings = Settings()
