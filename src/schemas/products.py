from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class Products(BaseModel):
    uuid: str | UUID
    price: float | int
    slug: str
    price_with_discount: float | int
    minute_count: int
    display_name: str
    discount_deadline: str | datetime
    discount: int

    class Config:
        from_attributes = True
