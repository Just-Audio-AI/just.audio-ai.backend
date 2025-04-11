from dataclasses import dataclass

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

    async def create_user_file(
        self, user_id: int, file_url: str, status: str, display_filename: str
    ):
        await self.user_file_repository.create_user_file(
            user_id=user_id,
            file_url=file_url,
            status=FileProcessingStatus.PROCESSING.value,
            display_filename=display_filename,
        )

    async def get_user_file(self, user_id: int, file_id: int):
        return await self.user_file_repository.get_user_file(user_id, file_id)
