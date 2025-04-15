from dataclasses import dataclass

from src.models import UserFile
from src.models.enums import FileProcessingStatus
from src.repository.user_file_repository import UserFileRepository


@dataclass
class UserFileService:
    user_file_repository: UserFileRepository

    async def make_user_file_completed(
        self, file_url: str, transcription_result: dict | str
    ) -> None:
        await self.user_file_repository.make_user_file_completed(
            file_url=file_url,
            status=FileProcessingStatus.COMPLETED.value,
            transcription=transcription_result,
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
        self, user_id: int, file_url: str, status: str, display_filename: str
    ):
        return await self.user_file_repository.create_user_file(
            user_id=user_id,
            file_url=file_url,
            status=status,
            display_filename=display_filename,
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
