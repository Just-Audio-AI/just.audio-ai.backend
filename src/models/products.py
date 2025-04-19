from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import uuid
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Products(Base):
    __tablename__ = "products"

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(comment="Название продукта, например '100 минут'")
    slug: Mapped[str] = mapped_column(comment="Слаг продукта, например '100-minutes'")
    price: Mapped[float] = mapped_column(comment="Цена без скидки")
    price_with_discount: Mapped[Optional[float]] = mapped_column(comment="Цена со скидкой")
    discount_deadline: Mapped[Optional[datetime]] = mapped_column(comment="Срок действия скидки")
    minute_count: Mapped[int] = mapped_column(comment="Количество минут")
    discount: Mapped[float] = mapped_column(comment="Процент скидки")
    is_active: Mapped[bool] = mapped_column(default=True, comment="Активен ли продукт")
    sort_order: Mapped[int] = mapped_column(default=0, comment="Порядок сортировки")
    is_subs: Mapped[bool] = mapped_column(default=False, comment="Подписка или разовая покупка")
    billing_cycle: Mapped[Optional[str]] = mapped_column(comment="Месяц, год")
    features: Mapped[Optional[str]] = mapped_column(comment="Список фич. Хранится как ['Фича 1', 'Фича 2']")
    is_can_select_gpt_model: Mapped[bool] = mapped_column(comment="Может выбирать модель GPT")
    cta_text: Mapped[Optional[str]] = mapped_column(comment="Текст кнопки")
    gpt_request_limit_one_file: Mapped[Optional[int]] = mapped_column(comment="Лимит запросов в GPT по одному файлу")
    vtt_file_ext_support: Mapped[bool] = mapped_column(comment="Поддерживается скачивание расшифровки в VTT формате")
    srt_file_ext_support: Mapped[bool] = mapped_column(comment="Поддерживается скачивание расшифровки в SRT формате")


class Transactions(Base):
    __tablename__ = "transactions"

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.uuid"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now)
    external_transcation_id: Mapped[str] = mapped_column(comment="Id транзакции в CloudPayments")
    status: Mapped[str] = mapped_column(comment="Статус транзакции")
    metainfo: Mapped[dict[str, Any]]
    price: Mapped[float]
    user_product_id: Mapped[UUID] = mapped_column(ForeignKey("user_products.uuid"))


class UserProducts(Base):
    __tablename__ = "user_products"

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    minute_count: Mapped[float] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now)
    amount: Mapped[float] = mapped_column(default=0, comment="Сумма оплаты")
    
    # Поля для подписок
    expires_at: Mapped[Optional[datetime]] = mapped_column(comment="Дата окончания подписке")
    is_subscription: Mapped[bool] = mapped_column(default=False, comment="Является ли записью подписки")
    subscription_id: Mapped[Optional[str]] = mapped_column(comment="ID подписки в CloudPayments")
    interval: Mapped[Optional[str]] = mapped_column(comment="Month или Year")
    is_active: Mapped[bool] = mapped_column(default=True, comment="Активна ли подписка")
    updated_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now)


class UserProductsToProductsM2M(Base):
    __tablename__ = "user_products_to_products"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.uuid"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    amount: Mapped[float]
    user_product: Mapped[UUID] = mapped_column(ForeignKey("user_products.uuid"))
