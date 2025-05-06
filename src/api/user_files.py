from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException, status, Response, Body
from fastapi.responses import StreamingResponse
import os
import json
from urllib.parse import urlparse

from src.dependency import get_user_file_service, get_current_user_id, get_file_service
from src.models.enums import FileProcessingStatus
from src.schemas.file import UserFileListResponse, UserFileListDetailResponse, TranscriptionUpdateRequest, \
    UserFileDetail
from src.service.file_service import FileService
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
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
    status: FileProcessingStatus | None = Query(
        None, description="Filter files by status"
    ),
):
    files = await user_file_service.get_user_files(current_user_id, status=status)
    return UserFileListResponse(items=files)


@router.get(
    "/detail",
    response_model=UserFileListDetailResponse,
)
async def get_user_files_detail(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
    status: FileProcessingStatus | None = Query(
        None, description="Filter files by status"
    ),
):
    files = await user_file_service.get_user_files(current_user_id, status=status)
    return UserFileListDetailResponse(items=files)


@router.get(
    "/{file_id}/detail",
    response_model=UserFileDetail
)
async def get_user_file_by_id_detail(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
    file_id: int,
):
    file = await user_file_service.get_user_file(user_id=current_user_id, file_ids=[file_id])
    return file[0]


@router.get(
    "/download",
    description="Download a file using its file key",
)
async def download_file(
    file_service: Annotated[FileService, Depends(get_file_service)],
    file_key: str = Query(..., description="File key to download (full URL path)"),
    stream: bool | None = Query(...)
):
    """
    Download a file using its file key.
    This endpoint fetches the file from the provided URL and serves it directly to the client.
    The user must own the file they're trying to download.
    """
    if not file_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File key is required",
        )

    parsed_url = urlparse(file_key)
    file_path = parsed_url.path
    filename = os.path.basename(file_path)

    # Determine content type based on file extension
    content_type = "application/octet-stream"  # Default content type
    if filename.endswith(".mp3"):
        content_type = "audio/mpeg"
    elif filename.endswith(".wav"):
        content_type = "audio/wav"
    elif filename.endswith(".ogg"):
        content_type = "audio/ogg"
    elif filename.endswith(".flac"):
        content_type = "audio/flac"

    response = file_service.get_file_from_bucket("public-file", file_key)
    # Create a generator function to stream the file content
    if not stream:
        return Response(
            content=response.read(),
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    async def file_stream():
        chunk_size = 64 * 1024  # 64KB
        while True:
            data = response.read(chunk_size)
            if not data:
                break
            yield data

    # Return a streaming response
    return StreamingResponse(
        file_stream(),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/{file_id}/transcription",
    status_code=status.HTTP_200_OK,
)
async def update_transcription(
    file_id: int,
    body: TranscriptionUpdateRequest,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
):
    """
    Update transcription data for a user file.
    
    Parameters:
    - file_id: ID of the file to update
    - body: Contains transcription_type and data
    """
    # Verify the file belongs to the user
    files = await user_file_service.get_user_file(current_user_id, [file_id])
    if not files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have access to it",
        )
    
    # Process the transcription based on type
    if body.transcription_type == "json":
        try:
            transcription_data = json.loads(body.data)
            await user_file_service.update_transcription_json(file_id, transcription_data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON data provided",
            )
    elif body.transcription_type == "text":
        await user_file_service.update_transcription_text(file_id, body.data)
    elif body.transcription_type == "vtt":
        await user_file_service.update_transcription_vtt(file_id, body.data)
    elif body.transcription_type == "srt":
        await user_file_service.update_transcription_srt(file_id, body.data)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transcription type. Must be one of: json, text, vtt, srt",
        )
    
    return {"status": "success"}
