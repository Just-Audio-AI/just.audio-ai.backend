from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.products import Products


@dataclass
class ProductsRepository:
    db: AsyncSession

    async def get_all_products(self) -> list[Products]:
        return (await self.db.execute(select(Products))).scalars().all()
