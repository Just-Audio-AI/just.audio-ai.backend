from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, computed_field, ConfigDict


class ProductInfo(BaseModel):
    uuid: UUID
    display_name: str
    minute_count: int
    price: float
    price_with_discount: float | None = None
    discount: float

    model_config = ConfigDict(from_attributes=True)


class TransactionResponse(BaseModel):
    uuid: UUID
    product_id: UUID
    user_id: int
    created_at: datetime
    price: float
    metainfo: dict

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def minute_count(self) -> int | None:
        """Get the minute count from metainfo if available"""
        return self.metainfo.get("minute_count") if self.metainfo else None

    @computed_field
    @property
    def transaction_id(self) -> int | None:
        """Get the payment system transaction ID if available"""
        return self.metainfo.get("transaction_id") if self.metainfo else None

    @computed_field
    @property
    def payment_status(self) -> str | None:
        """Get the payment status if available"""
        return self.metainfo.get("payment_status") if self.metainfo else None


class TransactionDetailResponse(BaseModel):
    transaction: TransactionResponse
    product: ProductInfo | None = None


class UserTransactionsResponse(BaseModel):
    transactions: list[TransactionResponse]
    total_count: int = Field(description="Total number of transactions")
