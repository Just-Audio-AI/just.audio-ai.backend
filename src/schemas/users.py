from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserResponse(BaseModel):
    id: int
    name: str | None = None
    email: EmailStr
    created_at: datetime | str
    minute_count: float | None = None

    model_config = ConfigDict(from_attributes=True)
