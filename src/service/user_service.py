from dataclasses import dataclass

from src.repository.user_products_repository import UserProductsRepository
from src.repository.user_repository import UserRepository
from src.schemas.users import UserResponse


@dataclass
class UserService:
    user_repository: UserRepository
    user_products_repository: UserProductsRepository

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        user_data = await self.user_repository.get_user_by_id_or_none(user_id)
        user_products_data = await self.user_products_repository.get_user_product(user_id)
        return UserResponse(
            id=user_id,
            name=user_data.name,
            email=user_data.email,
            created_at=user_data.created_at,
            minute_count=user_products_data.minute_count if user_products_data else None,
        )
