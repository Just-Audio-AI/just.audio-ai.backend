from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.models import UserProducts
from src.repository.user_products_repository import UserProductsRepository


@dataclass
class UserProductsService:
    user_products_repository: UserProductsRepository

    async def create_user_product(
        self,
        user_id: int,
        product_id: UUID,
        minute_count: float,
        amount: float,
    ) -> UserProducts:
        """
        Create a new user product record after successful payment
        """
        exist_user_product = await self.user_products_repository.get_user_product(
            user_id
        )
        if not exist_user_product:
            return await self.user_products_repository.create_user_product(
                user_id=user_id,
                minute_count=minute_count,
                amount=amount,
                product_id=product_id,
            )
        return await self.user_products_repository.update_user_product(
            user_id=user_id,
            user_product_id=exist_user_product.uuid,
            minute_count=minute_count + exist_user_product.minute_count,
            product_id=product_id,
        )

    async def deduct_minutes(self, user_id: int, seconds_used: int) -> UserProducts:
        """
        Deduct minutes from user's balance after file transcription
        Convert seconds to minutes (rounded up) for deduction
        """
        # Calculate minutes with ceiling to round up any partial minute
        minutes_to_deduct = seconds_used / 60.0  # Round up to nearest minute

        try:
            return await self.user_products_repository.deduct_minutes(
                user_id=user_id,
                minutes_to_deduct=minutes_to_deduct,
            )
        except ValueError as e:
            # Handle the case where user has no minutes
            raise ValueError(f"Failed to deduct minutes: {str(e)}")

    async def get_user_subscriptions(self, user_id: int) -> list[UserProducts]:
        """Получить все активные подписки пользователя"""
        return await self.user_products_repository.get_user_subscriptions(
            user_id=user_id,
            is_active=True,
        )

    async def get_subscription_by_external_subs_id(
        self, subscription_id: str
    ) -> UserProducts | None:
        """Получить подписку по ID в CloudPayments"""
        return await self.user_products_repository.get_subscription_by_external_subs_id(
            subscription_id
        )

    async def create_subscription(
        self,
        user_id: int,
        product_id: UUID,
        subscription_id: str | None,
        expires_at: datetime,
        amount: float,
        interval: str,
        minute_count: float,
    ) -> UserProducts:
        """Создать новую подписку"""
        return await self.user_products_repository.create_subscription_product(
            user_id=user_id,
            product_id=product_id,
            minute_count=minute_count,
            amount=amount,
            subscription_id=subscription_id,
            interval=interval,
            expires_at=expires_at,
        )

    async def update_subscription(
        self, minute_count: int, expires_at: datetime, user_subs_id: UUID
    ) -> UserProducts:
        return await self.user_products_repository.update_subscription(
            expires_at=expires_at,
            subscription_id=user_subs_id,
            minute_count=minute_count,
        )
