from typing import Annotated
from uuid import UUID
from datetime import datetime, UTC, timedelta

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
    SubscriptionId: str | None = None


class CloudPaymentsRecurrentCallback(BaseModel):
    Id: str
    TransactionId: int
    Amount: float  # Сумма операции
    AccountId: str  # ID пользователя
    Token: str  # Токен рекуррентного платежа
    Status: str  # Статус операции: Authorized, Completed, Declined
    StatusCode: int  # Код ошибки при отклонении операции
    Reason: str | None = None  # Причина отказа
    Data: dict = {}  # Содержит productId, userId, minuteCount из Data начального платежа
    InvoiceId: str | None = None  # Номер счета (необязательный параметр)
    TestMode: bool = False  # Тестовый режим
    
    # Параметры подписки
    SubscriptionId: str | None = None  # ID подписки в CloudPayments
    NextTransactionDate: str | None = None  # Дата следующего платежа


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
    Обработка callback'а от CloudPayments для обычных платежей
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

    callback = CloudPaymentsCallback(**data_dict)

    # Проверяем статус транзакции
    if callback.Status != "Completed":
        return {"code": 0}

    product_id = UUID(callback.Data["productId"])
    user_id = int(callback.Data["userId"])
    minute_count = float(callback.Data["minuteCount"])

    # Проверяем существование продукта
    product = await products_service.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    if callback.Status == "Reccurent":
        recurrent_data = callback.Data["CloudPayments"]["recurrent"]
        interval = recurrent_data["interval"]
        exist_subs = await user_products_service.get_subscription_by_id(callback.SubscriptionId) if callback.SubscriptionId else None
        if exist_subs and exist_subs.product_id == product.uuid:
            if interval == "Month":
                expires_at = exist_subs.expires_at + timedelta(days=31)
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Не корректный интервал {interval}")
            await user_products_service.update_user_products(
                user_id=user_id,
                expires_at=expires_at
            )
        else:
            if interval == "Month":
                expires_at = datetime.now(tz=UTC) + timedelta(days=31)
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Не корректный интервал {interval}")

            # Создаем запись о подписке
            user_products = await user_products_service.create_subscription(
                user_id=user_id,
                product_id=product_id,
                subscription_id=callback.Id,
                amount=recurrent_data.get("amount", callback.Amount),
                interval=interval,
                minute_count=product.minute_count,
                expires_at=expires_at
            )
    else:
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


@router.post("/cloudpayments/recurrent", status_code=status.HTTP_200_OK)
async def handle_cloudpayments_recurrent(
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
    Обработка вебхуков от CloudPayments для рекуррентных платежей
    """
    try:
        form_data = await request.form()
        data_dict = dict(form_data)

        # Преобразуем поле Data из JSON-строки в словарь, если оно есть
        if "Data" in data_dict and data_dict["Data"]:
            try:
                data_dict["Data"] = json.loads(data_dict["Data"])
            except json.JSONDecodeError:
                data_dict["Data"] = {}
        else:
            data_dict["Data"] = {}

        # Попытка создать модель из полученных данных
        callback = CloudPaymentsRecurrentCallback(**data_dict)

        # Логирование для отладки
        print(f"Received recurrent callback: {callback}")

        # Игнорируем неуспешные транзакции
        if callback.Status != "Completed":
            print(f"Ignoring non-completed transaction: {callback.Status} {callback.StatusCode} {callback.Reason}")
            return {"code": 0}

        # Получаем ID пользователя из AccountId
        try:
            user_id = int(callback.AccountId)
        except (ValueError, TypeError):
            print(f"Invalid AccountId: {callback.AccountId}")
            return {"code": 10}  # Некорректный идентификатор пользователя

        # Получаем данные о продукте
        # Если в Data есть productId, используем его, иначе ищем по подписке
        if "productId" in callback.Data:
            product_id = UUID(callback.Data["productId"])
            # Проверяем существование продукта
            product = await products_service.get_by_id(product_id)
            if not product:
                print(f"Product not found: {product_id}")
                return {"code": 11}  # Продукт не найден
            
            # Получаем количество минут
            minute_count = float(callback.Data.get("minuteCount", 0))
        else:
            # Если productId не указан, нужно получить его из подписки по SubscriptionId
            subscription = await user_products_service.get_subscription_by_id(callback.SubscriptionId)
            if not subscription:
                print(f"Subscription not found: {callback.SubscriptionId}")
                return {"code": 12}  # Подписка не найдена
                
            product_id = subscription.product_id
            product = await products_service.get_by_id(product_id)
            if not product:
                print(f"Product not found for subscription: {product_id}")
                return {"code": 11}  # Продукт не найден
                
            minute_count = float(product.minute_count)

        # 1. Создаем запись о покупке (продление подписки)
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
                "subscription_id": callback.SubscriptionId,
                "payment_status": callback.Status,
                "next_transaction_date": callback.NextTransactionDate,
                "recurrent": True,
                "minute_count": minute_count,
                "token": callback.Token,
            },
        )
        print(f"Successfully processed recurrent payment for user {user_id}, product {product_id}")
        return {"code": 0}  # Успешная обработка

    except Exception as e:
        print(f"Error processing recurrent payment callback: {str(e)}")
        return {"code": 13}  # Ошибка обработки


@router.post("/subscriptions/{subscription_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_subscription(
    subscription_id: str,
    user_products_service: Annotated[UserProductsService, Depends(get_user_products_service)],
) -> dict:
    """
    Отменить подписку пользователя
    """
    result = await user_products_service.cancel_subscription(subscription_id)
    if result:
        return {"success": True, "message": "Subscription canceled successfully"}
    else:
        return {"success": False, "message": "Failed to cancel subscription"}
