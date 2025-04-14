from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.dependency import get_products_service, get_user_products_service
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
    callback: CloudPaymentsCallback,
    products_service: Annotated[ProductsService, Depends(get_products_service)],
    user_products_service: Annotated[
        UserProductsService, Depends(get_user_products_service)
    ],
) -> dict:
    """
    Обработка callback'а от CloudPayments
    """
    # Проверяем статус транзакции
    if callback.Status != "Completed":
        return {"code": 0}

    try:
        # Получаем данные из callback'а
        product_id = UUID(callback.Data["productId"])
        user_id = int(callback.Data["userId"])
        minute_count = int(callback.Data["minuteCount"])

        # Проверяем существование продукта
        product = await products_service.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        # Создаем запись о покупке
        await user_products_service.create_user_product(
            user_id=user_id,
            minute_count=minute_count,
            transaction_id=callback.TransactionId,
            amount=callback.Amount,
        )

        return {"code": 0}  # Успешная обработка

    except Exception as e:
        print(f"Error processing payment callback: {str(e)}")
        return {"code": 13}  # Ошибка обработки
