from fastapi import APIRouter, Depends

from src.dependency import get_auth_service
from src.schemas.user import UserTokenResponse, UserTokenRequest
from src.service.auth import AuthService

router = APIRouter(
    tags=["firebase"],
    prefix="/auth",
)


@router.post(
    "/firebase",
    description="Создать пользователя по токену firebase",
    response_model=UserTokenResponse,
)
async def auth_by_firebase_token(
    body: UserTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.auth_by_firebase_token(token=body.token)
