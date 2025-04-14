from dataclasses import dataclass

from sqlalchemy import insert, select, update, delete
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

    async def update_files_status(self, file_ids: list[int], status: str) -> None:
        query = update(UserFile).where(UserFile.id.in_(file_ids)).values(status=status)
        await self.db.execute(query)
        await self.db.commit()

    async def create_user_file(
        self, user_id: int, file_url: str, status: str, display_filename: str
    ) -> UserFile:
        query = (
            insert(UserFile)
            .values(
                user_id=user_id,
                file_url=file_url,
                status=status,
                display_name=display_filename,
            )
            .returning(UserFile.id)
        )
        await self.db.execute(query)
        await self.db.commit()
        return await self.db.scalar(select(UserFile).where(UserFile.user_id == user_id))

    async def get_user_file(self, user_id: int, file_ids: list[int]) -> list[UserFile]:
        query = select(UserFile).where(
            UserFile.user_id == user_id, UserFile.id.in_(file_ids)
        )
        return (await self.db.scalars(query)).all()

    async def get_user_files(self, user_id: int, status: str = None) -> list[UserFile]:
        query = select(UserFile).where(UserFile.user_id == user_id)

        if status:
            query = query.where(UserFile.status == status)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_user_file(self, file_id: int) -> None:
        """
        Delete a user file from the database
        """
        query = delete(UserFile).where(UserFile.id == file_id)
        await self.db.execute(query)
        await self.db.commit()
