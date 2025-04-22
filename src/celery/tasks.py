from .celery_app import celery_app
from src.service.audio_processing import remove_noise
import os


@celery_app.task(name="process_audio")
def process_audio(file_path: str, remove_noise_flag: bool = True, remove_melody: bool = False) -> str:
    print(f"[TASK] Started processing: {file_path}")
    try:
        current_path = file_path

        if remove_noise_flag:
            current_path = remove_noise(current_path)

        # Здесь можно добавить remove_melody в будущем

        print(f"[TASK] Processing done: {current_path}")
        return current_path

    except Exception as e:
        print(f"[ERROR] Task failed: {str(e)}")
        raise e
