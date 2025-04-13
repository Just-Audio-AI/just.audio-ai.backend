from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.dependency import get_user_file_service
from src.models.enums import FileProcessingStatus
from src.schemas.file import UserFileListResponse, UserFileListDetailResponse
from src.service.user_file_service import UserFileService

router = APIRouter(
    tags=["user-files"],
    prefix="/user-files",
)


@router.get(
    "",
    response_model=UserFileListResponse,
)
async def get_user_files(
    user_id: int,
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
    status: FileProcessingStatus | None = Query(None, description="Filter files by status"),
):
    files = await user_file_service.get_user_files(user_id, status=status)
    return UserFileListResponse(items=files)


@router.get(
    "/detail",
    response_model=UserFileListDetailResponse,
)
async def get_user_files_detail(
    user_id: int,
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
    status: FileProcessingStatus | None = Query(None, description="Filter files by status"),
):
    files = await user_file_service.get_user_files(user_id, status=status)
    return UserFileListDetailResponse(items=files)
