import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

RNNOISE_MODEL = "src/ai_models/std.rnnn"


def remove_noise(input_path: str) -> str:
    input_path = Path(input_path)
    output_path = input_path.with_name(input_path.stem + "_denoised.wav")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-af",
        f"arnndn=m={RNNOISE_MODEL}",
        str(output_path),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"[ERROR] Noise removal failed: {e.stderr.decode()}")
        raise RuntimeError("Noise removal failed")

    return str(output_path)


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Возможные альтернативные имена файлов для разных стемов
STEM_ALIASES: dict[str, list[str]] = {
    'accompaniment': ['accompaniment', 'no_vocals', 'no-vocals', 'other'],
    'vocals': ['vocals']
}

def convert_to_wav(input_path: Path) -> Path:
    """
    Конвертирует файл в WAV, если он не в формате WAV.
    Возвращает путь к WAV-файлу (временный или оригинальный).
    """
    if input_path.suffix.lower() == '.wav':
        return input_path
    wav_path = input_path.with_name(f"{input_path.stem}_temp.wav")
    try:
        subprocess.run(
            ['ffmpeg', '-i', str(input_path), '-y', str(wav_path)],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        logger.info(f"Конвертирован в WAV: {wav_path}")
        return wav_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка конвертации в WAV: {e.stderr.decode()}")
        return input_path


def run_demucs(input_wav: Path, extract_stem: str, model: str = 'htdemucs') -> Path:
    """
    Запускает Demucs для двух стемов: выбранный стем extract_stem и его аккомпанемент.
    Возвращает путь к временной директории с результатами.
    """
    tmpdir = tempfile.mkdtemp(prefix='demucs_')
    cmd = [
        'python3', '-m', 'demucs',
        '-n', model,
        '--two-stems', extract_stem,
        '-o', tmpdir,
        str(input_wav)
    ]
    logger.info(f"Запуск Demucs: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return Path(tmpdir)


def remove_stem(
    input_path: str,
    extract_stem: str,
    desired_stem: str,
    suffix: str,
    model: str = 'htdemucs'
) -> str:
    """
    Убирает или извлекает нужный стем из аудио.

    :param input_path: путь к исходному файлу
    :param extract_stem: стем для извлечения Demucs ('vocals' и т.п.)
    :param desired_stem: базовое название файла .wav внутри результатов ('vocals' или 'accompaniment')
    :param suffix: суффикс для итогового файла
    :param model: модель Demucs
    :return: путь к итоговому файлу
    """
    path = Path(input_path)
    wav = convert_to_wav(path)
    tmpdir = None
    try:
        tmpdir = run_demucs(wav, extract_stem, model=model)
        # Ищем первый файл среди возможных алиасов
        aliases = STEM_ALIASES.get(desired_stem, [desired_stem])
        result_path = None
        for name in aliases:
            result_path = next(tmpdir.glob(f"**/{name}.wav"), None)
            if result_path:
                logger.info(f"Найден файл для стема '{desired_stem}': {name}.wav")
                break
        if not result_path:
            raise FileNotFoundError(
                f"Файл {desired_stem}.wav и альтернативные ({aliases}) не найдены в {tmpdir}"
            )
        output = path.with_name(f"{path.stem}{suffix}.wav")
        result_path.replace(output)
        logger.info(f"Сохранено: {output}")
        return str(output)
    finally:
        # Удаляем временный WAV
        if wav != path and wav.exists():
            wav.unlink()
        # Удаляем папку с результатами Demucs
        if tmpdir and tmpdir.exists():
            shutil.rmtree(tmpdir, ignore_errors=True)


def remove_vocals(input_path: str, model: str = 'htdemucs') -> str:
    """
    Удаляет вокал, оставляя только инструментал.
    """
    return remove_stem(
        input_path,
        extract_stem='vocals',
        desired_stem='accompaniment',
        suffix='_instrumental',
        model=model
    )


def remove_melody(input_path: str, model: str = 'htdemucs') -> str:
    """
    Извлекает вокал, убирая фонограмму.
    """
    return remove_stem(
        input_path,
        extract_stem='vocals',
        desired_stem='vocals',
        suffix='_vocals',
        model=model
    )
