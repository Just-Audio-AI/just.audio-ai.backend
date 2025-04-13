from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.dependency import get_auth_service
from src.exceptions import CodeExpiredExceptions, CodeNotFoundExceptions
from src.schemas import UserEmail, UserEmailCodeRequest, UserTokenResponse
from src.service.auth import AuthService

router = APIRouter(tags=["email"], prefix="/auth/email")


@router.post(
    "/code",
    description="Отправить код подтверждения почты",
)
async def email_auth(
    body: UserEmail, auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.send_auth_code(body.email)
    return Response(status_code=status.HTTP_200_OK, content="Code sent to email")

@router.post(
    "/verify-code",
    description="Подтверждение кода почты",
)
async def verify_code(
    body: UserEmailCodeRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    # try:
    user_data = await auth_service.verify_auth_code(body.email, body.code)
    return UserTokenResponse(
        user_id=user_data.get("user_id"), access_token=user_data.get("access_token")
    )

    # except (CodeNotFoundExceptions, CodeExpiredExceptions) as e:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)
    #
    # except Exception:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail="SERVICE UNAVAILABLE"
    #     )
