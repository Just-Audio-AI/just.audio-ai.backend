import tempfile
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, Response

from src.dependency import (
    get_audio_convert_service,
    get_file_service,
    get_user_file_service,
)
from src.service.audio_convert_service import AudioConvertService
from src.service.file_service import FileService
from src.service.user_file_service import UserFileService
from src.settings import settings

router = APIRouter(prefix="/audio/convert/file", tags=["audio-convert"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    user_id: int,
    file_service: Annotated[FileService, Depends(get_file_service)],
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
    file: UploadFile = File(...),
):
    uploaded_file_url = await file_service.handle_file_upload(file, user_id)
    await user_file_service.create_user_file(
        user_id, uploaded_file_url, status="processing", display_filename=file.filename
    )
    return Response(status_code=status.HTTP_201_CREATED)


@router.post("/transcription", status_code=status.HTTP_201_CREATED)
async def launch_transcription(
    user_id: int,
    file_id: int,
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
    audio_convert_service: Annotated[
        AudioConvertService, Depends(get_audio_convert_service)
    ],
):
    user_file = await user_file_service.get_user_file(user_id, file_id)
    if not user_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    audio_file_url = f"{settings.BASE_URL}/audio/convert/file/download/public-file/{user_file.file_url}"
    callback_url = f"{settings.whisper_ai_callback_url}/{user_file.file_url}"
    await audio_convert_service.convert_audio_to_text(
        audio_file_url=audio_file_url,
        response_format="json",
        language=None,  # Auto-detect language
        callback_url=callback_url,
    )
    return Response(status_code=status.HTTP_200_OK)


@router.get("/download/{bucket}/{user_id}/{file_name}")
async def download_file(
    file_service: Annotated[FileService, Depends(get_file_service)],
    bucket: str,
    user_id: str,
    file_name: str,
):
    if bucket not in file_service.get_public_bucket():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bucket not found"
        )

    file_key = user_id + "/" + file_name
    file_obj = file_service.get_file_from_bucket(bucket, file_key)

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"-{file_name}") as tmp_file:
        tmp_file.write(file_obj.read())
        tmp_file.flush()

        return FileResponse(
            path=tmp_file.name,
            filename=file_name,
            media_type="application/octet-stream",
        )


@router.post("/callback/{user_id}/{file_name}", status_code=status.HTTP_202_ACCEPTED)
async def callback_whishper(
    user_id: str,
    file_name: str,
    result: dict | str,
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
) -> Response:
    file_url = f"{user_id}/{file_name}"
    await user_file_service.make_user_file_completed(
        file_url=file_url, transcription_result=result
    )
    return Response(status_code=status.HTTP_202_ACCEPTED)
