import re
from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException, status, Response, Body, Request
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



@router.get("/download")
async def download_file(
    request: Request,
    file_service: Annotated[FileService, Depends(get_file_service)],
    file_key: str = Query(...),
    stream: bool | None = Query(...)
):
    if not file_key:
        raise HTTPException(status_code=404, detail="File key is required")

    # Извлекаем имя файла
    parsed = urlparse(file_key)
    filename = parsed.path.rsplit("/", 1)[-1]

    # Узнаём полный размер через stat_object
    full_size = file_service.get_object_size("public-file", file_key)

    # Разбираем заголовок Range
    range_header = request.headers.get("range")
    start = 0
    end = full_size - 1
    if range_header:
        m = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if not m:
            raise HTTPException(status_code=400, detail="Invalid Range header")
        start = int(m.group(1))
        if m.group(2):
            end = int(m.group(2))
        if start > end or end >= full_size:
            raise HTTPException(status_code=416, detail="Requested Range Not Satisfiable")

    length = end - start + 1

    # Определяем content_type по расширению
    content_type = "application/octet-stream"
    if filename.endswith(".mp3"):
        content_type = "audio/mpeg"
    elif filename.endswith(".wav"):
        content_type = "audio/wav"
    elif filename.endswith(".ogg"):
        content_type = "audio/ogg"
    elif filename.endswith(".flac"):
        content_type = "audio/flac"

    # Заголовки ответа
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": content_type,
    }

    status_code = status.HTTP_200_OK
    if range_header:
        headers.update({
            "Content-Range": f"bytes {start}-{end}/{full_size}",
            "Content-Length": str(length),
        })
        status_code = status.HTTP_206_PARTIAL_CONTENT
    else:
        headers["Content-Length"] = str(full_size)

    # Берём нужный диапазон из MinIO
    response = file_service.get_file_from_bucket(
        bucket_name="public-file",
        file_key=file_key,
        offset=start,
        length=length
    )

    # Если не stream и нет Range — возвращаем весь файл разом
    if not stream and not range_header:
        data = response.read()
        response.close()
        return Response(
            content=data,
            status_code=status_code,
            headers=headers,
            media_type=content_type
        )

    # Иначе — стримим чанками
    async def iterator():
        try:
            while True:
                chunk = response.read(64 * 1024)
                if not chunk:
                    break
                yield chunk
        finally:
            response.close()
            response.release_conn()

    return StreamingResponse(
        iterator(),
        status_code=status_code,
        headers=headers,
        media_type=content_type
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
