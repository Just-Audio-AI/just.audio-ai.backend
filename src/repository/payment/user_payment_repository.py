from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import insert, select, join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Transactions, Products


@dataclass
class UserPaymentRepository:
    db: AsyncSession

    async def get_user_transactions(self, user_id: int = None, transaction_id: UUID = None) -> list[Transactions]:
        """
        Get all user transactions with product information
        Optional filters by user_id or transaction_id
        """
        query = select(Transactions)
        
        if user_id is not None:
            query = query.where(Transactions.user_id == user_id)
            
        if transaction_id is not None:
            query = query.where(Transactions.uuid == transaction_id)
            
        query = query.order_by(Transactions.created_at.desc())
        return (await self.db.scalars(query)).all()
    
    async def get_transaction_with_product(self, transaction_id: UUID) -> tuple[Transactions, Products]:
        """
        Get a transaction with its associated product
        """
        query = (
            select(Transactions, Products)
            .join(Products, Transactions.product_id == Products.uuid)
            .where(Transactions.uuid == transaction_id)
        )
        result = await self.db.execute(query)
        return result.one()

    async def create_transaction(
        self,
        uuid: UUID,
        user_product_id: UUID,
        product_id: UUID,
        user_id: int,
        price: float,
        metainfo: dict,
    ) -> Transactions:
        """
        Create a transaction record in the database
        """
        query = insert(Transactions).values(
            uuid=uuid,
            product_id=product_id,
            user_id=user_id,
            price=price,
            metainfo=metainfo,
            user_product_id=user_product_id,
        ).returning(Transactions)

        result = await self.db.execute(query)
        await self.db.commit()
        return result.scalar_one()
