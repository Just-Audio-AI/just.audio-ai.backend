from dataclasses import dataclass

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.file import UserFile


@dataclass
class UserFileRepository:
    db: AsyncSession

    async def make_user_file_completed(
        self, file_url: str, status: str, transcription: dict | str
    ) -> None:
        query = (
            update(UserFile)
            .where(UserFile.file_url == file_url)
            .values(status=status, transcription=transcription)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def create_user_file(
        self, user_id: int, file_url: str, status: str, display_filename: str
    ) -> None:
        query = insert(UserFile).values(
            user_id=user_id,
            file_url=file_url,
            status=status,
            display_name=display_filename,
        )
        await self.db.execute(query)
        await self.db.commit()

    async def get_user_file(self, user_id: int, file_id: int) -> UserFile:
        query = select(UserFile).where(
            UserFile.user_id == user_id, UserFile.id == file_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
