from dataclasses import dataclass
from uuid import uuid4, UUID

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
                uuid=uuid4(),
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
