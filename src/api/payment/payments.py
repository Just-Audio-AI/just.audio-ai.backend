from typing import Annotated
from uuid import UUID
from datetime import datetime

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
import orjson as json
from src.dependency import (
    get_products_service,
    get_user_payment_service,
    get_user_products_service,
)
from src.schemas.payment import CloudPaymentsRecurrentCallback
from src.service.payment.user_payment import UserPaymentService
from src.service.products_service import ProductsService
from src.service.user_products_service import UserProductsService

router = APIRouter(
    tags=["payments"],
    prefix="/payments",
)


class CloudPaymentsCallback(BaseModel):
    TransactionId: int
    Amount: float
    Status: str
    Data: dict | None = None # Содержит productId, userId, minuteCount из виджета
    SubscriptionId: str | None = None
    AccountId: int


@router.post("/cloudpayments/callback", status_code=status.HTTP_200_OK)
async def handle_cloudpayments_callback(
    request: Request,
    products_service: Annotated[ProductsService, Depends(get_products_service)],
    user_products_service: Annotated[
        UserProductsService, Depends(get_user_products_service)
    ],
    user_payment_service: Annotated[
        UserPaymentService, Depends(get_user_payment_service)
    ],
) -> dict:
    """
    Обработка callback'а от CloudPayments для Pay уведомлений
    """

    form_data = await request.form()
    data_dict = dict(form_data)
    callback = CloudPaymentsCallback(**data_dict)

    exist_transaction = await user_payment_service.get_transaction_by_ext_id(external_id=str(callback.TransactionId))
    if exist_transaction:
        return {"code": 0}

    # Преобразуем поле Data из JSON-строки в словарь
    try:
        callback.Data = json.loads(data_dict["Data"])
    except (KeyError, json.JSONDecodeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неверный формат поля Data: {str(e)}",
        )

    # Проверяем статус транзакции
    if callback.Status != "Completed":
        return {"code": 0}

    product_id = UUID(callback.Data["productId"])
    user_id = callback.AccountId
    minute_count = float(callback.Data["minuteCount"])

    # Проверяем существование продукта
    product = await products_service.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    elif product.is_subs:
        subs_amount = int(callback.Data["CloudPayments"]["recurrent"]["amount"])
        interval = callback.Data["CloudPayments"]["recurrent"]["interval"]
        if interval == "Month":
            expires_at = datetime.now() + relativedelta(months=1)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Не корректный интервал {interval}",
            )

        user_products = await user_products_service.create_subscription(
            user_id=user_id,
            product_id=product.uuid,
            subscription_id=callback.SubscriptionId,
            amount=subs_amount or callback.Amount,
            expires_at=expires_at,
            interval=interval,
            minute_count=product.minute_count,
        )
    else:
        # 1. Создаем запись о покупке
        user_products = await user_products_service.create_user_product(
            user_id=user_id,
            minute_count=product.minute_count,
            amount=callback.Amount,
            product_id=product_id,
        )

    # 2. Создаем запись о транзакции
    await user_payment_service.create_transaction(
        product_id=product_id,
        user_id=user_id,
        price=callback.Amount,
        user_product_id=user_products.uuid,
        external_transaction_id=str(callback.TransactionId),
        status=callback.Status,
        metainfo={
            "transaction_id": callback.TransactionId,
            "minute_count": minute_count,
            "payment_status": callback.Status,
        },
    )
    return {"code": 0}  # Успешная обработка


@router.post("/cloudpayments/recurrent", status_code=status.HTTP_200_OK)
async def handle_cloudpayments_recurrent(
    request: Request,
    user_payment_service: Annotated[
        UserPaymentService, Depends(get_user_payment_service)
    ],
) -> dict:
    """
    Обработка вебхуков от CloudPayments для рекуррентных платежей
    """
    form_data = await request.form()
    data_dict = dict(form_data)
    # Попытка создать модель из полученных данных
    callback = CloudPaymentsRecurrentCallback(**data_dict)
    await user_payment_service.handle_recurrent_success_callback(callback)
    return {"code": 0}  # Успешная обработка
