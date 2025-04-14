from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.products import UserProducts


@dataclass
class UserProductsRepository:
    db: AsyncSession

    async def create_user_product(
        self,
        uuid: UUID,
        user_id: int,
        minute_count: int,
        transaction_id: int,
        amount: float,
    ) -> None:
        """
        Create a new user product record in the database
        """
        query = insert(UserProducts).values(
            uuid=uuid,
            user_id=user_id,
            minute_count=minute_count,
            transaction_id=transaction_id,
            amount=amount,
        )
        await self.db.execute(query)
        await self.db.commit()
