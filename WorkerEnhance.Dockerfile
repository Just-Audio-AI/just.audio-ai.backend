FROM python:3.12

ENV DEBIAN_FRONTEND=noninteractive

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    python3 \
    python3-pip \
    python3-venv \
    git \
    wget \
    && apt-get clean

# Создание рабочей директории и установка Python-зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка PyTorch (CPU-only)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Установка Demucs и поддержки soundfile
RUN pip install demucs soundfile

# Копируем исходники
COPY ./src ./src

# Команда по умолчанию — запуск Celery worker
CMD ["celery", "-A", "src.celery.celery_app", "worker", "-Q", "enhance", "--concurrency=2", "--loglevel=info"]
