from pydantic import BaseModel, EmailStr


class UserTokenResponseSchema(BaseModel):
    user_id: int
    access_token: str




class User(BaseModel):
    username: str | None = None
    email: EmailStr
    avatar: str | None = None


class UserCreate(User):
    google_token: str | None = None


class UserUpdate(User):
    pass


class UserOut(BaseModel):
    id: int
    username: str
    avatar: str


class Token(BaseModel):
    id: int
    token: str


class TokenPayload(BaseModel):
    user_id: int = None


class UserSettingsResponse(BaseModel):
    user_id: int
    is_onboardings_ends: bool
    timezone: int | None = None
