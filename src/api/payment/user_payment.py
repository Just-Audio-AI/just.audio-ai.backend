from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.dependency import get_user_payment_service, get_products_service
from src.schemas.transaction import (
    UserTransactionsResponse,
    TransactionResponse,
    TransactionDetailResponse,
    ProductInfo,
)
from src.service.payment.user_payment import UserPaymentService
from src.service.products_service import ProductsService

router = APIRouter(prefix="/payment/user-payment", tags=["payment"])


@router.get("/transactions", response_model=UserTransactionsResponse)
async def get_user_transactions(
    user_id: int,
    user_payment_service: Annotated[
        UserPaymentService, Depends(get_user_payment_service)
    ],
):
    """
    Get all transactions for a specific user
    """
    transactions = await user_payment_service.get_user_transactions(user_id=user_id)
    return UserTransactionsResponse(
        transactions=[TransactionResponse.model_validate(tx) for tx in transactions],
        total_count=len(transactions),
    )


@router.get("/transactions/{transaction_id}", response_model=TransactionDetailResponse)
async def get_transaction_details(
    transaction_id: UUID,
    user_payment_service: Annotated[
        UserPaymentService, Depends(get_user_payment_service)
    ],
    products_service: Annotated[ProductsService, Depends(get_products_service)],
):
    """
    Get detailed information about a specific transaction, including product details
    """
    try:
        transaction_with_product = (
            await user_payment_service.get_transaction_with_product(transaction_id)
        )
        if not transaction_with_product.transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )

        # If product wasn't joined, try to get it separately
        product = transaction_with_product.product
        if not product:
            product = await products_service.get_by_id(
                transaction_with_product.transaction.product_id
            )

        return TransactionDetailResponse(
            transaction=TransactionResponse.model_validate(
                transaction_with_product.transaction
            ),
            product=ProductInfo.model_validate(product),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction not found: {str(e)}",
        )
