from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.products import UserProducts, UserProductsToProductsM2M


@dataclass
class UserProductsRepository:
    db: AsyncSession

    async def create_user_product(
        self,
        uuid: UUID,
        user_id: int,
        minute_count: float,
        product_id: UUID,
        amount: float,
    ) -> UserProducts:
        """
        Create a new user product record in the database
        """
        query = insert(UserProducts).values(
            uuid=uuid,
            user_id=user_id,
            minute_count=minute_count,
            amount=amount,
        ).returning(UserProducts)
        created_user_product = (await self.db.execute(query)).scalar_one()
        await self.__create_user_products_to_products(
            user_id=user_id,
            product_id=product_id,
            amount=created_user_product.amount,
            user_product=created_user_product.uuid,
        )
        await self.db.commit()
        return created_user_product

    async def get_user_product(self, user_id: int) -> UserProducts:
        query = select(UserProducts).where(UserProducts.user_id == user_id)
        return await self.db.scalar(query)

    async def update_user_product(
        self,
        user_id: int,
        minute_count: float,
        user_product_id: UUID,
        product_id: UUID,
    ) -> UserProducts:
        query = update(UserProducts).where(
            UserProducts.uuid == user_product_id,
            UserProducts.user_id == user_id
        ).values(minute_count=minute_count).returning(UserProducts)
        updated_user_products = (await self.db.execute(query)).scalar_one()
        user_products_to_products_exist = select(UserProductsToProductsM2M).where(
            UserProductsToProductsM2M.user_id == user_id,
            UserProductsToProductsM2M.product_id == product_id,
            UserProductsToProductsM2M.user_product == updated_user_products.uuid,
        )
        result = (await self.db.execute(user_products_to_products_exist)).scalar_one_or_none()
        if not result:
            await self.__create_user_products_to_products(
                user_id=user_id,
                product_id=product_id,
                amount=updated_user_products.amount,
                user_product=updated_user_products.uuid,
            )
            await self.db.commit()
        return updated_user_products

    async def __create_user_products_to_products(
        self,
        user_id: int,
        product_id: UUID,
        amount: float,
        user_product: UUID,
    ):
        user_products_to_products_query = insert(UserProductsToProductsM2M).values(
            user_id=user_id,
            product_id=product_id,
            amount=amount,
            user_product=user_product
        )
        await self.db.execute(user_products_to_products_query)
        await self.db.commit()
        
    async def deduct_minutes(self, user_id: int, minutes_to_deduct: float) -> UserProducts:
        """
        Deduct minutes from user's balance after file transcription
        """
        user_product = await self.get_user_product(user_id)
        if not user_product:
            raise ValueError(f"User {user_id} has no product with minutes")
            
        new_minute_count = max(0, user_product.minute_count - minutes_to_deduct)
        
        query = update(UserProducts).where(
            UserProducts.uuid == user_product.uuid,
            UserProducts.user_id == user_id
        ).values(minute_count=new_minute_count).returning(UserProducts)
        
        updated_user_product = (await self.db.execute(query)).scalar_one()
        await self.db.commit()
        return updated_user_product
