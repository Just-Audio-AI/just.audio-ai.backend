from dataclasses import dataclass
from datetime import datetime
import logging
from uuid import UUID

from fastapi import HTTPException
from starlette import status

from src.models import UserProducts
from src.repository.user_products_repository import UserProductsRepository
from src.schemas.products import UserProductPlanResponse


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

    async def deduct_minutes(self, user_id: int, seconds_used: float) -> UserProducts:
        """
        Deduct minutes from user's balance after file transcription
        Convert seconds to minutes (rounded up) for deduction
        """
        # Calculate minutes with ceiling to round up any partial minute
        minutes_to_deduct = seconds_used / 60.0  # Round up to minute

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

    async def get_user_product_plan(
        self, user_id: int
    ) -> UserProductPlanResponse:
        logging.debug(f"Getting product plan for user: {user_id}")
        user_products = await self.user_products_repository.get_user_subscriptions(user_id, True)
        if not user_products:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        user_product = user_products[0]
        product = await self.user_products_repository.get_product_by_id(user_product.product_id)
        return UserProductPlanResponse(
            product_id=user_product.product_id,
            minute_count_limit=product.minute_count,
            minute_count_used=int(user_product.minute_count_used),
            expires_at=user_product.expires_at,
            amount=user_product.amount,
            is_can_select_gpt_model=product.is_can_select_gpt_model,
            is_can_remove_melody=product.is_can_remove_melody,
            is_can_remove_vocal=product.is_can_remove_vocal,
            is_can_remove_noise=product.is_can_remove_noise,
            is_can_enhance_audio=product.is_can_improve_audio,
            gpt_request_limit_one_file=product.gpt_request_limit_one_file,
            vtt_file_ext_support=product.vtt_file_ext_support,
            srt_file_ext_support=product.srt_file_ext_support,
            is_subscription=product.is_subs,
            is_can_use_gpt=product.is_can_use_gpt
        )
