from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    name: str | None = None
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
