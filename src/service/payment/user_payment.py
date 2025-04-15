from dataclasses import dataclass
from uuid import UUID, uuid4

from src.models import Transactions, Products
from src.repository.payment.user_payment_repository import UserPaymentRepository


class TransactionWithProduct:
    """Helper class to combine transaction and product data"""

    transaction: Transactions
    product: Products | None = None

    def __init__(self, transaction: Transactions, product: Products | None = None):
        self.transaction = transaction
        self.product = product


@dataclass
class UserPaymentService:
    user_payment_repository: UserPaymentRepository

    async def get_user_transactions(self, user_id: int) -> list[Transactions]:
        """Get all transactions for a user"""
        return await self.user_payment_repository.get_user_transactions(user_id)

    async def get_transaction_with_product(
        self, transaction_id: UUID
    ) -> TransactionWithProduct:
        """Get a transaction with its product details"""
        try:
            transaction, product = (
                await self.user_payment_repository.get_transaction_with_product(
                    transaction_id
                )
            )
            return TransactionWithProduct(transaction=transaction, product=product)
        except Exception:
            # If join fails, try to get just the transaction
            transactions = await self.user_payment_repository.get_user_transactions(
                user_id=None, transaction_id=transaction_id
            )
            if not transactions:
                return TransactionWithProduct(transaction=None)
            return TransactionWithProduct(transaction=transactions[0])

    async def create_transaction(
        self,
        product_id: UUID,
        user_product_id: UUID,
        user_id: int,
        price: float,
        metainfo: dict,
    ) -> Transactions:
        return await self.user_payment_repository.create_transaction(
            uuid=uuid4(),
            product_id=product_id,
            user_product_id=user_product_id,
            user_id=user_id,
            price=price,
            metainfo=metainfo,
        )
