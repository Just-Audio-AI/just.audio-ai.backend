from pydantic import BaseModel


class UserTokenResponseSchema(BaseModel):
    user_id: int
    access_token: str
