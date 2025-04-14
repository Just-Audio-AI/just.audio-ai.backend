from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependency import get_user_service
from src.models.users import User
from src.schemas.users import UserResponse
from src.service.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/detail", response_model=UserResponse)
async def get_user_info(
    user_id: int, user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    """
    Get current user information
    """
    return await user_service.get_user_by_id(user_id)
