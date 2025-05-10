import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import noisereduce as nr
from fastapi import HTTPException
from pedalboard.io import AudioFile
from pedalboard import Pedalboard, NoiseGate, Compressor, Gain, LowShelfFilter, HighShelfFilter

from src.facade.user_file_service_facade import FileServiceFacade, UserFileServiceFacade
from src.models import FileImproveAudioStatus

PRESET_CONFIGS = {
    "smart_enhancement": {
        "description": "Умное улучшение речи — универсальный режим для подавления шума и усиления голоса.",
        "chain": Pedalboard([
            NoiseGate(threshold_db=-30, ratio=1.5, release_ms=250),
            Compressor(threshold_db=-16, ratio=2.5),
            Gain(gain_db=6)
        ])
    },

    "clear_speech": {
        "description": "Ясная речь — подходит для записи голоса в домашних условиях или на диктофон.",
        "chain": Pedalboard([
            NoiseGate(threshold_db=-30, ratio=1.5, release_ms=250),
            Compressor(threshold_db=-16, ratio=2.5),
            Gain(gain_db=8)
        ])
    },

    "quiet_voice_boost": {
        "description": "Тихий голос — усиливает и делает более разборчивым слабый голос.",
        "chain": Pedalboard([
            LowShelfFilter(cutoff_frequency_hz=200, gain_db=4.0, q=0.7),
            Compressor(threshold_db=-20, ratio=2.0),
            Gain(gain_db=5)
        ])
    },

    "lecture_optimization": {
        "description": "Записи лекций — подавляет фоновый шум и делает речь преподавателя четче.",
        "chain": Pedalboard([
            NoiseGate(threshold_db=-32, ratio=1.8, release_ms=300),
            Compressor(threshold_db=-18, ratio=2.5),
            Gain(gain_db=6)
        ])
    },

    "expressive_speech": {
        "description": "Выразительная речь — делает голос ярче и выделяет высокие частоты.",
        "chain": Pedalboard([
            Compressor(threshold_db=-15, ratio=3.0),
            HighShelfFilter(cutoff_frequency_hz=6000, gain_db=3.0, q=0.7),
            Gain(gain_db=7)
        ])
    },

    "noisy_environment_cleanup": {
        "description": "Шумное окружение — агрессивная фильтрация шума для улицы, транспорта и т.д.",
        "chain": Pedalboard([
            NoiseGate(threshold_db=-35, ratio=2.0, release_ms=350),
            Compressor(threshold_db=-18, ratio=2.8),
            Gain(gain_db=9)
        ])
    },

    "video_voice_enhancement": {
        "description": "Озвучка для видео — делает голос более выразительным для видео и подкастов.",
        "chain": Pedalboard([
            HighShelfFilter(cutoff_frequency_hz=4000, gain_db=1.5, q=1.0),
            Compressor(threshold_db=-17, ratio=2.2),
            Gain(gain_db=6)
        ])
    }
}


async def enhance_audio_async(file_id: int, user_id: int, file_url: str, preset: str = "quiet_voice_boost") -> dict:
    from pydub import AudioSegment
    from pydub.utils import make_chunks

    file_service = await FileServiceFacade.get_file_service()
    user_file_service = await UserFileServiceFacade.get_user_file_service()
    await user_file_service.update_enhance_audio_status(file_id, FileImproveAudioStatus.PROCESSING)

    tmp_dir = tempfile.mkdtemp()
    filename = Path(file_url).name
    input_file_path = os.path.join(tmp_dir, filename)
    converted_path = os.path.join(tmp_dir, "converted.wav")
    output_path = os.path.join(tmp_dir, "enhanced.wav")

    try:
        with open(input_file_path, "wb") as f:
            s3_file = file_service.get_file_from_bucket("public-file", file_url)
            f.write(s3_file.read())
        logging.info(f"[TASK] Downloaded: {input_file_path}")

        # Convert to 16kHz mono WAV
        subprocess.run(["ffmpeg", "-y", "-i", input_file_path, "-ar", "16000", "-ac", "1", converted_path], check=True)

        audio_segment = AudioSegment.from_wav(converted_path)
        chunk_length_ms = 300_000  # 5 minutes in ms
        if len(audio_segment) > chunk_length_ms:
            logging.info("[INFO] Audio longer than 5 minutes. Splitting...")
            chunks = make_chunks(audio_segment, chunk_length_ms)
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_path = os.path.join(tmp_dir, f"chunk_{i}.wav")
                chunk.export(chunk_path, format="wav")

                with AudioFile(chunk_path) as f:
                    chunk_audio = f.read(f.frames)
                    sr = f.samplerate

                reduced = nr.reduce_noise(y=chunk_audio, sr=sr, stationary=True, prop_decrease=0.75)
                board = PRESET_CONFIGS[preset]["chain"]
                if not board:
                    raise HTTPException(status_code=400, detail=f"Unknown preset: {preset}")

                enhanced = board(reduced, sr)
                chunk_enhanced_path = os.path.join(tmp_dir, f"enhanced_chunk_{i}.wav")
                with AudioFile(chunk_enhanced_path, 'w', sr, enhanced.shape[0]) as f:
                    f.write(enhanced)

                processed_chunks.append(AudioSegment.from_wav(chunk_enhanced_path))

            final_audio = sum(processed_chunks)
            final_audio.export(output_path, format="wav")

        else:
            with AudioFile(converted_path) as f:
                audio = f.read(f.frames)
                sample_rate = f.samplerate

            reduced_noise = nr.reduce_noise(y=audio, sr=sample_rate, stationary=True, prop_decrease=0.75)
            board = PRESET_CONFIGS[preset]["chain"]
            if not board:
                raise HTTPException(status_code=400, detail=f"Unknown preset: {preset}")

            enhanced_audio = board(reduced_noise, sample_rate)
            with AudioFile(output_path, 'w', sample_rate, enhanced_audio.shape[0]) as f:
                f.write(enhanced_audio)

        s3_key = f"enhanced/enhanced_{Path(filename).stem}.wav"
        with open(output_path, "rb") as f_out:
            await file_service.upload_file_to_s3(user_id=user_id, filename=s3_key, file_obj=f_out)

        await user_file_service.update_enhance_audio_status(file_id, FileImproveAudioStatus.COMPLETED)
        await user_file_service.update_enhance_audio_url(file_id, f"{user_id}/{s3_key}")

        return {
            "file_id": file_id,
            "processed_file_url": s3_key,
            "processing_type": "enhance",
        }

    except Exception as e:
        logging.exception(f"[ERROR] Enhancement failed: {e}")
        await user_file_service.update_enhance_audio_status(file_id, FileImproveAudioStatus.FAILED)
        raise

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logging.info(f"[CLEANUP] Removed temp dir: {tmp_dir}")
