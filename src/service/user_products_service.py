from dataclasses import dataclass
from uuid import uuid4

from src.repository.user_products_repository import UserProductsRepository


@dataclass
class UserProductsService:
    user_products_repository: UserProductsRepository

    async def create_user_product(
        self,
        user_id: int,
        minute_count: int,
        transaction_id: int,
        amount: float,
    ) -> None:
        """
        Create a new user product record after successful payment
        """
        await self.user_products_repository.create_user_product(
            uuid=uuid4(),
            user_id=user_id,
            minute_count=minute_count,
            transaction_id=transaction_id,
            amount=amount,
        )
