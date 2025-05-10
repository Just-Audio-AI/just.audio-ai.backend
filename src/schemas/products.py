from datetime import datetime
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class BillingCycle(str, Enum):
    MONTH = "month"
    YEAR = "year"


class ProductResponse(BaseModel):
    """Schema for product response"""

    uuid: UUID = Field(description="Unique identifier of the product")
    display_name: str = Field(description="Display name of the product")
    slug: str = Field(description="URL-friendly name of the product")
    price: float = Field(description="Original price of the product in RUB", gt=-1)
    price_with_discount: float | None = Field(
        None, description="Discounted price of the product in RUB", gt=0
    )
    discount_deadline: datetime | None = Field(
        None, description="Deadline for the discount offer"
    )
    minute_count: int = Field(
        description="Number of minutes available in this product", gt=-2
    )
    discount: float = Field(description="Discount percentage", ge=0, le=100)
    is_subs: bool = Field(
        default=False,
        description="Whether this is a subscription or a one-time purchase",
    )
    billing_cycle: BillingCycle | None = Field(
        None, description="Billing cycle: month or year"
    )
    features: list[str] | None = Field(
        None, description="List of features included in the product"
    )
    cta_text: str | None = Field(None, description="Call to action button text")
    is_can_select_gpt_model: bool = Field(
        default=False, description="Whether the user can select GPT model"
    )
    gpt_request_limit_one_file: int | None = Field(
        None, description="Limit of GPT requests per file"
    )
    vtt_file_ext_support: bool = Field(
        default=False, description="Support for VTT file format download"
    )
    srt_file_ext_support: bool = Field(
        default=False, description="Support for SRT file format download"
    )

    model_config = ConfigDict(from_attributes=True)

    def is_discount_active(self) -> bool:
        """Check if product has active discount"""
        if not self.price_with_discount or not self.discount_deadline:
            return False
        return self.discount_deadline > datetime.utcnow()

    @property
    def final_price(self) -> float:
        """Get final price considering discount"""
        if self.is_discount_active():
            return self.price_with_discount
        return self.price


class UserProductPlanResponse(BaseModel):
    product_id: UUID
    minute_count_limit: int
    minute_count_used: int
    gpt_request_limit_one_file: int
    is_can_select_gpt_model: int
    vtt_file_ext_support: int
    srt_file_ext_support: int
    is_can_remove_melody: int
    is_can_remove_vocal: int
    is_can_remove_noise: int
    is_can_use_gpt: bool
    is_subscription: bool
    amount: float
    expires_at: datetime
