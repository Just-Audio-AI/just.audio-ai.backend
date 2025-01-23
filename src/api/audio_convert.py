import io
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, Response

from src.dependency import get_file_service, get_user_file_service
from src.service.file_service import FileService
from src.service.user_file_service import UserFileService

router = APIRouter(prefix="/audio/convert", tags=["audio-convert"])

@router.post("/file", status_code=status.HTTP_201_CREATED)
async def add_file_for_convert(
    user_id: int,
    file_service: Annotated[FileService, Depends(get_file_service)],
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
    file: UploadFile = File(...),
):
    uploaded_file_url = await file_service.handle_file_upload(file, user_id)
    await user_file_service.create_user_file(user_id, uploaded_file_url, status='processed', display_filename="test.mp4")
    return Response(status_code=status.HTTP_201_CREATED)


@router.get("/file/download/{bucket}/{user_id}/{file_name}")
async def download_file(
    file_service: Annotated[FileService, Depends(get_file_service)],
    bucket: str,
    user_id: str,
    file_name: str,
):
    if bucket not in file_service.get_public_bucket():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bucket not found")
    file_key = user_id+"/"+file_name
    file_obj = file_service.get_file_from_bucket(bucket, file_key)
    file_stream = io.BytesIO(file_obj.read())

    return StreamingResponse(
        file_stream,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )

@router.post("file/callback", status_code=status.HTTP_202_ACCEPTED)
async def callback_whishper(
    result: dict | str,
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
) -> None:
    await user_file_service.make_user_file_completed(result)
