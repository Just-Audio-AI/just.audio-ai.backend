from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
import orjson as json
from src.dependency import (
    get_products_service,
    get_user_payment_service,
    get_user_products_service,
)
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
    Data: dict  # Содержит productId, userId, minuteCount из виджета


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
    Обработка callback'а от CloudPayments
    """

    form_data = await request.form()
    data_dict = dict(form_data)

    # Преобразуем поле Data из JSON-строки в словарь
    try:
        data_dict["Data"] = json.loads(data_dict["Data"])
    except (KeyError, json.JSONDecodeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неверный формат поля Data: {str(e)}",
        )

    try:
        callback = CloudPaymentsCallback(**data_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Ошибка валидации данных: {str(e)}",
        )

    # Проверяем статус транзакции
    if callback.Status != "Completed":
        return {"code": 0}

    # try:
    # Получаем данные из callback'а
    product_id = UUID(callback.Data["productId"])
    user_id = int(callback.Data["userId"])
    minute_count = float(callback.Data["minuteCount"])

    # Проверяем существование продукта
    product = await products_service.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # 1. Создаем запись о покупке
    user_products = await user_products_service.create_user_product(
        user_id=user_id,
        minute_count=minute_count,
        amount=callback.Amount,
        product_id=product_id,
    )
    # 2. Создаем запись о транзакции
    await user_payment_service.create_transaction(
        product_id=product_id,
        user_id=user_id,
        price=callback.Amount,
        user_product_id=user_products.uuid,
        metainfo={
            "transaction_id": callback.TransactionId,
            "minute_count": minute_count,
            "payment_status": callback.Status,
        },
    )

    return {"code": 0}  # Успешная обработка
    #
    # except Exception as e:
    #     print(f"Error processing payment callback: {str(e)}")
    #     return {"code": 13}  # Ошибка обработки
