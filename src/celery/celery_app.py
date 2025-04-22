from celery import Celery
import os

# Настройки брокера (Redis)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Инициализация Celery
celery_app = Celery("audio_ai")
celery_app.conf.broker_url = redis_url
celery_app.conf.result_backend = redis_url
