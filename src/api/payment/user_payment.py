from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependency import get_user_payment_service
from src.service.payment.user_payment import UserPaymentService

router = APIRouter(prefix="/payment/user-payment", tags=["payment"])


@router.get("/transaction")
async def get_user_transaction(
    user_id: int,
    user_payment_service: Annotated[
        UserPaymentService, Depends(get_user_payment_service)
    ],
):
    return user_payment_service.get_user_transactions(user_id=user_id)
