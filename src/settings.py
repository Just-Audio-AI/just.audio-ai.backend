from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(validation_alias="DATABASE_URL", default="postgresql+asyncpg://postgres:password@0.0.0.0:5432/app_db")

settings = Settings()