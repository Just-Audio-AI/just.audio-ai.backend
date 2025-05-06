from dataclasses import dataclass

from src.models import UserFile
from src.models.enums import FileProcessingStatus, FileRemoveMelodyStatus, FileRemoveNoiseStatus, FileRemoveVocalStatus
from src.repository.user_file_repository import UserFileRepository


@dataclass
class UserFileService:
    user_file_repository: UserFileRepository

    async def make_user_file_completed(
        self, 
        file_url: str, 
        transcription_result: dict | str,
        transcription_text: str | None = None,
        transcription_vtt: str | None = None,
        transcription_srt: str | None = None
    ) -> None:
        await self.user_file_repository.make_user_file_completed(
            file_url=file_url,
            status=FileProcessingStatus.COMPLETED.value,
            transcription=transcription_result,
            transcription_text=transcription_text,
            transcription_vtt=transcription_vtt,
            transcription_srt=transcription_srt,
        )

    async def update_file_duration(self, file_id: int, duration: int) -> None:
        """
        Update the duration of a file in seconds
        """
        await self.user_file_repository.update_file_duration(file_id, duration)

    async def update_files_status(
        self, file_ids: list[int], status: FileProcessingStatus
    ) -> None:
        await self.user_file_repository.update_files_status(
            file_ids=file_ids,
            status=status.value,
        )

    async def create_user_file(
        self,
        user_id: int,
        file_url: str,
        status: str,
        display_filename: str,
        file_size: int = None,
        mime_type: str = None,
    ):
        return await self.user_file_repository.create_user_file(
            user_id=user_id,
            file_url=file_url,
            status=status,
            display_filename=display_filename,
            file_size=file_size,
            mime_type=mime_type,
        )

    async def get_user_file(self, user_id: int, file_ids: list[int]) -> list[UserFile]:
        return await self.user_file_repository.get_user_file(user_id, file_ids)

    async def get_user_files(self, user_id: int, status: FileProcessingStatus = None):
        status_value = status.value if status else None
        return await self.user_file_repository.get_user_files(user_id, status_value)

    async def delete_user_file(self, file_id: int) -> None:
        """
        Delete a user file from the database
        """
        await self.user_file_repository.delete_user_file(file_id)

    async def get_user_file_by_url(self, file_url: str):
        """
        Get a user file by its URL
        """
        return await self.user_file_repository.get_user_file_by_url(file_url)

    async def update_noise_removed_url(
        self, file_id: int, removed_noise_url: str
    ) -> None:
        """
        Update the URL of the noise-removed file
        """
        await self.user_file_repository.update_noise_removed_url(
            file_id, removed_noise_url
        )

    async def update_melody_removed_status(self, file_id: int, status: FileRemoveMelodyStatus):
        await self.user_file_repository.update_melody_removed_status(
            file_id, status
        )

    async def update_noise_removed_status(self, file_id: int, status: FileRemoveNoiseStatus):
        await self.user_file_repository.update_noise_removed_status(
            file_id, status
        )

    async def update_vocals_removed_status(self, file_id: int, status: FileRemoveVocalStatus):
        await self.user_file_repository.update_vocals_removed_status(
            file_id, status
        )

    async def update_melody_removed_url(
        self, file_id: int, removed_melody_url: str
    ) -> None:
        """
        Update the URL of the melody-removed file (vocals only)
        """
        await self.user_file_repository.update_melody_removed_url(
            file_id, removed_melody_url
        )

    async def update_vocals_removed_url(
        self, file_id: int, removed_vocals_url: str
    ) -> None:
        """
        Update the URL of the vocals-removed file (instrumental only)
        """
        await self.user_file_repository.update_vocals_removed_url(
            file_id, removed_vocals_url
        )

    async def update_transcription_json(self, file_id: int, transcription_data: dict) -> None:
        """
        Update the JSON transcription data for a file
        """
        await self.user_file_repository.update_transcription_json(file_id, transcription_data)

    async def update_transcription_text(self, file_id: int, text: str) -> None:
        """
        Update the text transcription for a file
        """
        await self.user_file_repository.update_transcription_text(file_id, text)

    async def update_transcription_vtt(self, file_id: int, vtt: str) -> None:
        """
        Update the VTT transcription for a file
        """
        await self.user_file_repository.update_transcription_vtt(file_id, vtt)

    async def update_transcription_srt(self, file_id: int, srt: str) -> None:
        """
        Update the SRT transcription for a file
        """
        await self.user_file_repository.update_transcription_srt(file_id, srt)
