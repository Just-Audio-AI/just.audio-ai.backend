from celery import shared_task

from src.celery.celery_app import celery_app
from src.service.audio_processing import remove_noise, remove_melody, remove_vocals
from src.service.enhance_audio import enhance_audio_async
import tempfile
import os
import logging
from pathlib import Path
import asyncio
from src.models.enums import FileProcessingStatus, FileRemoveNoiseStatus, FileRemoveMelodyStatus, FileRemoveVocalStatus
from src.facade.user_file_service_facade import UserFileServiceFacade, FileServiceFacade


@celery_app.task(name="process_audio")
def process_audio(
    file_id: int, user_id: int, file_url: str, remove_noise_flag: bool = False,
    remove_melody_flag: bool = False, remove_vocals_flag: bool = False
) -> dict:
    logging.info(f"[TASK] Started processing file_id: {file_id}, file_url: {file_url}")
    try:
        # Run the async operations in a new event loop
        return asyncio.run(
            process_audio_async(
                file_id, user_id, file_url, 
                remove_noise_flag, remove_melody_flag, remove_vocals_flag
            )
        )
    except Exception as e:
        logging.error(f"[ERROR] Task failed: {str(e)}")
        # Обработка ошибки Celery-задачи - обновляем статус на failed
        try:
            # Создаем новый event loop для асинхронных вызовов
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Получаем сервис и обновляем статус в зависимости от типа операции
            user_file_service = loop.run_until_complete(UserFileServiceFacade.get_user_file_service())
            
            if remove_noise_flag:
                loop.run_until_complete(
                    user_file_service.update_noise_removed_status(
                        file_id, status=FileRemoveNoiseStatus.FAILED)
                )
            elif remove_melody_flag:
                loop.run_until_complete(
                    user_file_service.update_melody_removed_status(
                        file_id, status=FileRemoveMelodyStatus.FAILED)
                )
            elif remove_vocals_flag:
                loop.run_until_complete(
                    user_file_service.update_vocals_removed_status(
                        file_id, status=FileRemoveVocalStatus.FAILED)
                )
            
            loop.close()
        except Exception as inner_e:
            logging.error(f"[ERROR] Failed to update error status: {str(inner_e)}")
        
        raise e


@shared_task(name="enhance_audio", queue="enhance")
def enhance_audio_task(file_id: int, user_id: int, file_url: str, preset: str) -> dict:
    return asyncio.run(enhance_audio_async(file_id, user_id, file_url, preset=preset))


async def process_audio_async(
    file_id: int, user_id: int, file_url: str, 
    remove_noise_flag: bool = False,
    remove_melody_flag: bool = False,
    remove_vocals_flag: bool = False
) -> dict:
    """Asynchronous implementation of the audio processing"""
    # Initialize services with async DB session
    file_service = await FileServiceFacade.get_file_service()
    user_file_service = await UserFileServiceFacade.get_user_file_service()

    # Определяем тип операции для обработки ошибок
    processing_type = None
    if remove_noise_flag:
        processing_type = "noise"
    elif remove_melody_flag:
        processing_type = "melody"
    elif remove_vocals_flag:
        processing_type = "vocals"

    try:
        # Extract filename from URL
        filename = Path(file_url).name

        # Create temp directory for processing
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Download file from S3
            input_file_path = os.path.join(tmp_dir, filename)
            with open(input_file_path, "wb") as f:
                file_obj = file_service.get_file_from_bucket("public-file", file_url)
                f.write(file_obj.read())

            logging.info(f"[TASK] Downloaded file: {input_file_path}")

            # Process file based on flags
            output_file_path = None
            
            if remove_noise_flag:
                await user_file_service.update_noise_removed_status(file_id, status=FileRemoveNoiseStatus.PROCESSING)
                output_file_path = remove_noise(input_file_path)
                logging.info(f"[TASK] Noise removed: {output_file_path}")
                processing_type = "noise"
            elif remove_melody_flag:
                await user_file_service.update_melody_removed_status(file_id, status=FileRemoveMelodyStatus.PROCESSING)
                output_file_path = remove_melody(input_file_path)
                logging.info(f"[TASK] Melody removed (vocals only): {output_file_path}")
                processing_type = "melody"
            elif remove_vocals_flag:
                await user_file_service.update_vocals_removed_status(file_id, status=FileRemoveVocalStatus.PROCESSING)
                output_file_path = remove_vocals(input_file_path)
                logging.info(f"[TASK] Vocals removed (instrumental only): {output_file_path}")
                processing_type = "vocals"

            # Upload processed file back to S3
            if output_file_path:
                output_filename = Path(output_file_path).name
                output_key = f"{output_filename}"

                with open(output_file_path, "rb") as f:
                    uploaded_file_url = await file_service.upload_file_to_s3(
                        f, user_id, f"{output_key}"
                    )

                # Update UserFile with the new URL based on processing type
                if processing_type == "noise":
                    await user_file_service.update_noise_removed_url(file_id, uploaded_file_url)
                    await user_file_service.update_noise_removed_status(file_id, status=FileRemoveNoiseStatus.COMPLETED)
                elif processing_type == "melody":
                    await user_file_service.update_melody_removed_url(file_id, uploaded_file_url)
                    await user_file_service.update_melody_removed_status(file_id, status=FileRemoveMelodyStatus.COMPLETED)
                elif processing_type == "vocals":
                    await user_file_service.update_vocals_removed_url(file_id, uploaded_file_url)
                    await user_file_service.update_vocals_removed_status(file_id, status=FileRemoveVocalStatus.COMPLETED)

                # Update file status to completed
                await user_file_service.update_files_status(
                    [file_id], FileProcessingStatus.COMPLETED
                )

                logging.info(f"[TASK] Uploaded processed file: {uploaded_file_url}")
                return {"file_id": file_id, "processed_file_url": uploaded_file_url, "processing_type": processing_type}
        await user_file_service.user_file_repository.db.close()
        return {"file_id": file_id, "status": "no_processing_needed"}
    except Exception as e:
        # Обрабатываем ошибку и устанавливаем статус failed
        logging.error(f"[ERROR] Processing error: {str(e)}")
        
        try:
            # Устанавливаем статус failed в зависимости от типа операции
            if processing_type == "noise":
                await user_file_service.update_noise_removed_status(file_id, status=FileRemoveNoiseStatus.FAILED)
            elif processing_type == "melody":
                await user_file_service.update_melody_removed_status(file_id, status=FileRemoveMelodyStatus.FAILED)
            elif processing_type == "vocals":
                await user_file_service.update_vocals_removed_status(file_id, status=FileRemoveVocalStatus.FAILED)
            
            # Обновляем общий статус файла
            await user_file_service.update_files_status(
                [file_id], FileProcessingStatus.COMPLETED
            )
        except Exception as inner_e:
            logging.error(f"[ERROR] Failed to update error status: {str(inner_e)}")
        
        # Закрываем соединение с БД
        try:
            await user_file_service.user_file_repository.db.close()
        except:
            pass
        
        # Пробрасываем ошибку дальше
        raise e
