from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ProductResponse(BaseModel):
    """Schema for product response"""

    uuid: UUID = Field(description="Unique identifier of the product")
    display_name: str = Field(description="Display name of the product")
    slug: str = Field(description="URL-friendly name of the product")
    price: float = Field(description="Original price of the product in RUB", gt=0)
    price_with_discount: Optional[float] = Field(
        None, description="Discounted price of the product in RUB", gt=0
    )
    discount_deadline: Optional[datetime] = Field(
        None, description="Deadline for the discount offer"
    )
    minute_count: int = Field(
        description="Number of minutes available in this product", gt=0
    )
    discount: float = Field(description="Discount percentage", ge=0, le=100)

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
