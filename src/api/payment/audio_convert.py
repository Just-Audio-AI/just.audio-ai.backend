import os
import tempfile
from pathlib import Path
import uuid

import ffmpeg

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
    BackgroundTasks,
)
from fastapi.responses import FileResponse, Response, JSONResponse

from src.dependency import (
    get_audio_convert_service,
    get_file_service,
    get_user_file_service,
    get_user_products_service,
)
from src.models.enums import FileProcessingStatus
from src.schemas.file import FileTranscriptionRequest
from src.service.audio_convert_service import AudioConvertService
from src.settings import settings

from src.service.file_service import FileService
from src.service.user_file_service import UserFileService
from src.service.user_products_service import UserProductsService

router = APIRouter(prefix="/audio/convert/file", tags=["audio-convert"])

ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    user_id: int,
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service),
    user_file_service: UserFileService = Depends(get_user_file_service),
):
    # Validate file extension
    extension = Path(file.filename).suffix.lower() if file.filename else ""
    if (
        extension not in ALLOWED_AUDIO_EXTENSIONS
        and extension not in ALLOWED_VIDEO_EXTENSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Allowed formats: {', '.join(ALLOWED_AUDIO_EXTENSIONS.union(ALLOWED_VIDEO_EXTENSIONS))}",
        )

    # Create a temporary directory to process files
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Save the original file
        temp_file_path = os.path.join(tmp_dir, f"original_{uuid.uuid4()}{extension}")
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Process file based on its type
        final_file_path = temp_file_path
        duration_seconds = 0

        # If it's a video, extract the audio
        if extension in ALLOWED_VIDEO_EXTENSIONS:
            audio_output_path = os.path.join(tmp_dir, f"audio_{uuid.uuid4()}.wav")
            try:
                # Use ffmpeg to extract audio
                ffmpeg.input(temp_file_path).output(
                    audio_output_path, acodec="pcm_s16le", ac=1, ar="16k"
                ).run(quiet=True, overwrite_output=True)
                final_file_path = audio_output_path
            except ffmpeg.Error as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error extracting audio from video: {str(e)}",
                )

        # Get file duration using ffmpeg
        try:
            probe = ffmpeg.probe(final_file_path)
            duration_seconds = int(float(probe["format"]["duration"]))
        except ffmpeg.Error as e:
            # If duration detection fails, log but continue
            print(f"Error detecting file duration: {str(e)}")

        # Upload file to S3
        # try:
        # Get original filename without extension for display
        original_name = Path(file.filename).stem if file.filename else "file"
        display_filename = (
            f"{original_name}.wav"
            if extension in ALLOWED_VIDEO_EXTENSIONS
            else file.filename
        )

        # Upload to S3 and save record in database
        with open(final_file_path, "rb") as f:
            uploaded_file_url = await file_service.upload_file_to_s3(
                f, user_id, Path(final_file_path).name
            )

        # Create a user file record
        file_record = await user_file_service.create_user_file(
            user_id,
            uploaded_file_url,
            status=FileProcessingStatus.UPLOADED.value,
            display_filename=display_filename,
        )

        # Update the file duration if detected
        if duration_seconds > 0:
            await user_file_service.update_file_duration(
                file_record.id, duration_seconds
            )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "file_id": file_record.id,
                "file_url": uploaded_file_url,
                "status": file_record.status,
                "display_filename": display_filename,
                "duration_seconds": duration_seconds,
            },
        )
        #
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail=f"Error uploading file: {str(e)}",
        #     )


@router.post("/transcription", status_code=status.HTTP_201_CREATED)
async def launch_transcription(
    background_tasks: BackgroundTasks,
    user_id: int,
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
    audio_convert_service: Annotated[
        AudioConvertService, Depends(get_audio_convert_service)
    ],
    body: FileTranscriptionRequest,
):
    user_files = await user_file_service.get_user_file(user_id, body.file_ids)
    if not user_files:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # Update files status to PROCESSING before starting transcription
    await user_file_service.update_files_status(
        body.file_ids, FileProcessingStatus.PROCESSING
    )

    # Add transcription tasks to background tasks
    for user_file in user_files:
        audio_file_url = f"{settings.BASE_URL}/audio/convert/file/download/public-file/{user_file.file_url}"
        callback_url = f"{settings.whisper_ai_callback_url}/{user_file.file_url}"

        background_tasks.add_task(
            audio_convert_service.convert_audio_to_text,
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
    file_service: Annotated[FileService, Depends(get_file_service)],
    user_products_service: Annotated[
        UserProductsService, Depends(get_user_products_service)
    ],
) -> Response:
    file_url = f"{user_id}/{file_name}"

    # Get the file record
    user_file = await user_file_service.get_user_file_by_url(file_url)
    if not user_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    # Save transcription result
    await user_file_service.make_user_file_completed(
        file_url=file_url, transcription_result=result
    )

    # Deduct minutes from user's balance if file has duration
    if user_file.duration and user_file.duration > 0:
        try:
            await user_products_service.deduct_minutes(
                user_id=int(user_id), seconds_used=user_file.duration
            )
        except ValueError as e:
            # Log the error but don't fail the request
            print(f"Error deducting minutes: {str(e)}")

    # Delete the audio file from S3
    try:
        await file_service.delete_file_from_s3(user_id, file_name)
    except Exception as e:
        # Log the error but don't fail the request since we already have the transcription
        print(f"Error deleting file from S3: {str(e)}")

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    user_id: int,
    file_service: Annotated[FileService, Depends(get_file_service)],
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)],
) -> Response:
    # Get file info before deletion
    file = await user_file_service.get_user_file(user_id, [file_id])
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    file = file[0]  # Get first file since we queried by single ID

    # Delete file from S3
    try:
        await file_service.delete_file_from_s3(str(user_id), Path(file.file_url).name)
    except Exception as e:
        print(f"Error deleting file from S3: {str(e)}")
        # Continue with DB deletion even if S3 deletion fails

    # Delete record from database
    await user_file_service.delete_user_file(file_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
