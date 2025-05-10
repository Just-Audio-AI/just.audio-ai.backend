from dataclasses import dataclass

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import FileRemoveVocalStatus, FileRemoveMelodyStatus, FileRemoveNoiseStatus
from src.models.file import UserFile


@dataclass
class UserFileRepository:
    db: AsyncSession

    async def make_user_file_completed(
        self, 
        file_url: str, 
        status: str, 
        transcription: dict | str,
        transcription_text: str | None = None,
        transcription_vtt: str | None = None,
        transcription_srt: str | None = None
    ) -> None:
        query = (
            update(UserFile)
            .where(UserFile.file_url == file_url)
            .values(
                status=status, 
                transcription=transcription,
                transcription_text=transcription_text,
                transcription_vtt=transcription_vtt,
                transcription_srt=transcription_srt
            )
        )
        await self.db.execute(query)
        await self.db.commit()

    async def update_file_duration(self, file_id: int, duration: int) -> None:
        """
        Update the duration of a file in seconds
        """
        query = update(UserFile).where(UserFile.id == file_id).values(duration=duration)
        await self.db.execute(query)
        await self.db.commit()

    async def update_files_status(self, file_ids: list[int], status: str) -> None:
        query = update(UserFile).where(UserFile.id.in_(file_ids)).values(status=status)
        await self.db.execute(query)
        await self.db.commit()

    async def create_user_file(
        self,
        user_id: int,
        file_url: str,
        status: str,
        display_filename: str,
        file_size: int = None,
        mime_type: str = None,
    ) -> UserFile:
        query = (
            insert(UserFile)
            .values(
                user_id=user_id,
                file_url=file_url,
                status=status,
                display_name=display_filename,
                file_size=file_size,
                mime_type=mime_type,
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

    async def get_user_file_by_url(self, file_url: str) -> UserFile:
        """
        Get a user file by its URL
        """
        query = select(UserFile).where(UserFile.file_url == file_url)
        return await self.db.scalar(query)

    async def update_noise_removed_url(
        self, file_id: int, removed_noise_url: str
    ) -> None:
        """
        Update the URL of the noise-removed file
        """
        query = (
            update(UserFile)
            .where(UserFile.id == file_id)
            .values(removed_noise_file_url=removed_noise_url)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def update_melody_removed_url(
        self, file_id: int, removed_melody_url: str
    ) -> None:
        """
        Update the URL of the melody-removed file (vocals only)
        """
        query = (
            update(UserFile)
            .where(UserFile.id == file_id)
            .values(removed_melody_file_url=removed_melody_url)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def update_vocals_removed_url(
        self, file_id: int, removed_vocals_url: str
    ) -> None:
        """
        Update the URL of the vocals-removed file (instrumental only)
        """
        query = (
            update(UserFile)
            .where(UserFile.id == file_id)
            .values(removed_vocals_file_url=removed_vocals_url)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def update_vocals_removed_status(self, file_id: int, status: FileRemoveVocalStatus):
        query = (
            update(UserFile)
            .where(UserFile.id == file_id)
            .values(removed_vocal_file_status=status.value)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def update_melody_removed_status(self, file_id: int, status: FileRemoveMelodyStatus):
        query = (
            update(UserFile)
            .where(UserFile.id == file_id)
            .values(removed_melody_file_status=status.value)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def update_noise_removed_status(self, file_id: int, status: FileRemoveNoiseStatus):
        query = (
            update(UserFile)
            .where(UserFile.id == file_id)
            .values(removed_noise_file_status=status.value)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def update_transcription_json(self, file_id: int, transcription_data: dict) -> None:
        """
        Update the JSON transcription data for a file
        """
        query = (
            update(UserFile)
            .where(UserFile.id == file_id)
            .values(transcription=transcription_data)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def update_transcription_text(self, file_id: int, text: str) -> None:
        """
        Update the text transcription for a file
        """
        query = (
            update(UserFile)
            .where(UserFile.id == file_id)
            .values(transcription_text=text)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def update_transcription_vtt(self, file_id: int, vtt: str) -> None:
        """
        Update the VTT transcription for a file
        """
        query = (
            update(UserFile)
            .where(UserFile.id == file_id)
            .values(transcription_vtt=vtt)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def update_transcription_srt(self, file_id: int, srt: str) -> None:
        """
        Update the SRT transcription for a file
        """
        query = (
            update(UserFile)
            .where(UserFile.id == file_id)
            .values(transcription_srt=srt)
        )
        await self.db.execute(query)
        await self.db.commit()
