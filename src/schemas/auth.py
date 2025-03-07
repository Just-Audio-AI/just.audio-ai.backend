from pydantic import BaseModel, EmailStr


class UserEmailCodeRequest(BaseModel):
    email: EmailStr
    code: int


class UserEmail(BaseModel):
    email: EmailStr
