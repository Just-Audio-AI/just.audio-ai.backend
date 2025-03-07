from fastapi import APIRouter, Depends, HTTPException, status

from src.dependency import get_auth_service
from src.schemas import UserTokenResponseSchema
from src.service.auth import AuthService

router = APIRouter(
    tags=["firebase"],
    prefix="/auth/firebase",
)


@router.post(
    "/auth-by-firebase-token",
    description="Создать пользователя по токену firebase",
    response_model=UserTokenResponseSchema,
)
async def auth_by_firebase_token(
    token: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    user_data = await auth_service.auth_by_firebase_token(token=token)
    return UserTokenResponseSchema(user_id=user_data.get("user_id"), access_token=user_data.get("access_token"))
