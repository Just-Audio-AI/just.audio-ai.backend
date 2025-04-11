from fastapi import APIRouter, Depends
from typing import Annotated

from src.dependency import get_user_file_service
from src.service.user_file_service import UserFileService

router = APIRouter(
    tags=["user-files"],
    prefix="/user-files",
)


async def get_user_files(
    user_id: int,
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
):
    return await user_file_service.get_user_files(user_id)
