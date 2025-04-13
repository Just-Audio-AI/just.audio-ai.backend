from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Transactions


@dataclass
class UserPaymentRepository:
    db: AsyncSession

    async def get_user_transactions(self, user_id: int) -> list[Transactions]:
        query = select(Transactions).where(Transactions.user_id == user_id)
        return (await self.db.scalars(query)).all()
