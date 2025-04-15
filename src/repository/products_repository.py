from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.products import Products


@dataclass
class ProductsRepository:
    db: AsyncSession

    async def get_all_products(self) -> list[Products]:
        return (
            (await self.db.execute(select(Products).order_by(Products.sort_order)))
            .scalars()
            .all()
        )

    async def get_by_id(self, product_id: UUID) -> Products:
        return (await self.db.execute(select(Products).where(Products.uuid == product_id))).scalar_one()