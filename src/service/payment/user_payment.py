from dataclasses import dataclass

from src.models import Transactions
from src.repository.payment.user_payment_repository import UserPaymentRepository


@dataclass
class UserPaymentService:
    user_payment_repository: UserPaymentRepository

    async def get_user_transactions(self, user_id: int) -> list[Transactions]:
        return await self.user_payment_repository.get_user_transactions(user_id)
