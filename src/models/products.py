from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Products(Base):
    __tablename__ = "products"

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    display_name: Mapped[str]  # например "100 минут"
    slug: Mapped[str]
    price: Mapped[float]  # цена без скидки
    price_with_discount: Mapped[Optional[float]]  # цена со скидкой
    discount_deadline: Mapped[Optional[datetime]]  # срок действия скидки
    minute_count: Mapped[int]  # количество минут
    discount: Mapped[float]  # процент скидки
    is_active: Mapped[bool] = mapped_column(default=True)  # активен ли продукт
    sort_order: Mapped[int] = mapped_column(default=0)  # порядок сортировки


class Transactions(Base):
    __tablename__ = "transactions"

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.uuid"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    metainfo: Mapped[dict[str, Any]]
    price: Mapped[float]


class UserProducts(Base):
    __tablename__ = "user_products"

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    minute_count: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    transaction_id: Mapped[int]  # ID транзакции из CloudPayments
    amount: Mapped[float]  # Сумма оплаты
