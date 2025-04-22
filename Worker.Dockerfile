FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg \
    python3 \
    python3-pip \
    python3-venv \
    git \
    wget \
    && apt-get clean

# Создание директории и установка зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

# Скачиваем модель RNNoise
RUN mkdir -p /app/src/models && \
    wget -O /app/src/ai_models/std.rnnn https://github.com/richardpl/arnndn-models/raw/master/std.rnnn

# Команда по умолчанию — запуск Celery worker
CMD ["celery", "-A", "celery.celery_app", "worker", "--loglevel=info"]
