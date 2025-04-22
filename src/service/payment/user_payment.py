from dataclasses import dataclass
from uuid import UUID, uuid4

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from starlette import status

from src.models import Transactions, Products
from src.repository.payment.user_payment_repository import UserPaymentRepository
from src.repository.products_repository import ProductsRepository
from src.schemas.payment import CloudPaymentsRecurrentCallback
from src.service.user_products_service import UserProductsService


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
    user_products_service: UserProductsService
    product_repository: ProductsRepository

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
        external_transaction_id: str,
        status: str,
    ) -> Transactions:
        return await self.user_payment_repository.create_transaction(
            uuid=uuid4(),
            product_id=product_id,
            user_product_id=user_product_id,
            user_id=user_id,
            price=price,
            metainfo=metainfo,
            status=status,
            external_transaction_id=external_transaction_id,
        )

    async def handle_recurrent_success_callback(
        self, callback: CloudPaymentsRecurrentCallback
    ):
        interval = callback.Interval
        exist_subs = (
            await self.user_products_service.get_subscription_by_external_subs_id(
                callback.Id
            )
        )
        product = await self.product_repository.get_by_id(
            product_id=exist_subs.product_id
        )
        if interval == "Month":
            expires_at = exist_subs.expires_at + relativedelta(months=1)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Не корректный интервал {interval}",
            )
        await self.user_products_service.update_subscription(
            expires_at=expires_at,
            user_subs_id=exist_subs.uuid,
            minute_count=exist_subs.minute_count + product.minute_count,
        )
