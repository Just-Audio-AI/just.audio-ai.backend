from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from src.models.file import UserFile


@dataclass
class UserFileRepository:
    db: AsyncSession

    async def make_user_file_completed(self):
        pass

    async def create_user_file(self, user_id: int, file_url: str, status: str, display_filename: str) -> None:
        query = insert(UserFile).values(
            user_id=user_id,
            file_url=file_url,
            status=status,
            display_name=display_filename,

        )