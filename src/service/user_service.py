from dataclasses import dataclass

from src.models import User
from src.repository.user_repository import UserRepository

@dataclass
class UserService:
    user_repository: UserRepository

    async def get_user_by_id(self, user_id: int) -> User:
        return await self.user_repository.get_user_by_id_or_none(user_id)
