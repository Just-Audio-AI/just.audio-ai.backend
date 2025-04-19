from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.products import UserProducts, UserProductsToProductsM2M


@dataclass
class UserProductsRepository:
    db: AsyncSession

    async def create_user_product(
        self,
        user_id: int,
        minute_count: float,
        amount: float,
        product_id: UUID,
    ) -> UserProducts:
        user_products = UserProducts(
            uuid=uuid4(),
            user_id=user_id,
            minute_count=minute_count,
            amount=amount,
        )

        self.db.add(user_products)
        await self.db.commit()
        await self.db.refresh(user_products)

        user_products_to_products = UserProductsToProductsM2M(
            user_id=user_id,
            product_id=product_id,
            amount=amount,
            user_product=user_products.uuid,
        )

        self.db.add(user_products_to_products)
        await self.db.commit()

        return user_products

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
        query = (
            update(UserProducts)
            .where(
                UserProducts.uuid == user_product_id, UserProducts.user_id == user_id
            )
            .values(minute_count=minute_count)
            .returning(UserProducts)
        )
        updated_user_products = (await self.db.execute(query)).scalar_one()
        user_products_to_products_exist = select(UserProductsToProductsM2M).where(
            UserProductsToProductsM2M.user_id == user_id,
            UserProductsToProductsM2M.product_id == product_id,
            UserProductsToProductsM2M.user_product == updated_user_products.uuid,
        )
        result = (
            await self.db.execute(user_products_to_products_exist)
        ).scalar_one_or_none()
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
            user_product=user_product,
        )
        await self.db.execute(user_products_to_products_query)
        await self.db.commit()

    async def deduct_minutes(
        self, user_id: int, minutes_to_deduct: float
    ) -> UserProducts:
        """
        Deduct minutes from user's balance after file transcription
        """
        user_product = await self.get_user_product(user_id)
        if not user_product:
            raise ValueError(f"User {user_id} has no product with minutes")

        new_minute_count = max(0, user_product.minute_count - minutes_to_deduct)

        query = (
            update(UserProducts)
            .where(
                UserProducts.uuid == user_product.uuid, UserProducts.user_id == user_id
            )
            .values(minute_count=new_minute_count)
            .returning(UserProducts)
        )

        updated_user_product = (await self.db.execute(query)).scalar_one()
        await self.db.commit()
        return updated_user_product

    # Методы для работы с подписками
    async def create_subscription_product(
        self,
        user_id: int,
        minute_count: float,
        amount: float,
        product_id: UUID,
        subscription_id: str,
        expires_at: datetime,
        interval: str = "Month",
    ) -> UserProducts:
        """Создать запись о продукте с подпиской"""
        user_products = UserProducts(
            uuid=uuid4(),
            user_id=user_id,
            minute_count=minute_count,
            amount=amount,
            is_subscription=True,
            subscription_id=subscription_id,
            interval=interval,
            is_active=True,
            expires_at=expires_at,
        )

        self.db.add(user_products)
        await self.db.commit()
        await self.db.refresh(user_products)

        user_products_to_products = UserProductsToProductsM2M(
            user_id=user_id,
            product_id=product_id,
            amount=amount,
            user_product=user_products.uuid,
        )

        self.db.add(user_products_to_products)
        await self.db.commit()

        return user_products

    async def get_user_subscriptions(
        self, user_id: int, is_active: Optional[bool] = None
    ) -> List[UserProducts]:
        """Получить все подписки пользователя"""
        query = (
            select(UserProducts)
            .where(UserProducts.user_id == user_id)
            .where(UserProducts.is_subscription == True)
        )
        
        if is_active is not None:
            query = query.where(UserProducts.is_active == is_active)
            
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_subscription_by_id(self, subscription_id: str) -> Optional[UserProducts]:
        """Получить подписку по ID в системе CloudPayments"""
        query = select(UserProducts).where(
            UserProducts.subscription_id == subscription_id,
            UserProducts.is_subscription == True,
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update_subscription(
        self,
        subscription_id: str,
        next_payment_date: Optional[datetime] = None,
        is_active: Optional[bool] = None,
        updated_at: Optional[datetime] = None,
    ) -> bool:
        """Обновить подписку"""
        subscription = await self.get_subscription_by_id(subscription_id)
        if not subscription:
            return False
            
        update_values = {}
        
        if next_payment_date is not None:
            update_values[UserProducts.next_payment_date] = next_payment_date
            
        if is_active is not None:
            update_values[UserProducts.is_active] = is_active
            
        if updated_at is not None:
            update_values[UserProducts.updated_at] = updated_at
        else:
            update_values[UserProducts.updated_at] = datetime.now()
            
        if not update_values:
            return True  # Нет изменений
            
        query = (
            update(UserProducts)
            .where(UserProducts.subscription_id == subscription_id)
            .values(**update_values)
        )
        
        await self.db.execute(query)
        await self.db.commit()
        
        return True
