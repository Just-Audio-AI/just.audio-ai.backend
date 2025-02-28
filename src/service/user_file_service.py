from dataclasses import dataclass

from src.repository.user_file_repository import UserFileRepository


@dataclass
class UserFileService:
    user_file_repository: UserFileRepository

    async def make_user_file_completed(self, result: dict | str):
        await self.user_file_repository.make_user_file_completed()

    async def create_user_file(self, user_id: int, file_url: str, status: str, display_filename: str):
        await self.user_file_repository.create_user_file(user_id, file_url, status, display_filename)

    async def get_user_files(self, user_id: int):
        pass