from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Products(Base):
    __tablename__ = 'products'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    display_name: Mapped[str]
    slug: Mapped[str]
    price: Mapped[float]
    price_with_discount: Mapped[Optional[float]]
    discount_deadline: Mapped[Optional[datetime]]
    minute_count: Mapped[int]
    discount: Mapped[float]

class Transactions(Base):
    __tablename__ = 'transactions'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey('products.uuid'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    metainfo: Mapped[dict[str, Any]]
    price: Mapped[float]

class UserProducts(Base):
    __tablename__ = 'user_products'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    minute_count: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
