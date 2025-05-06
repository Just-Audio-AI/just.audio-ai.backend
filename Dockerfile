FROM python:3.13
LABEL authors="magomedov_sm"

WORKDIR /app
COPY ./requirements.txt ./

RUN apt-get update && apt-get install -y ffmpeg
# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта в рабочую директорию
COPY ./start.sh ./
COPY ./src ./src
COPY ./main.py ./
COPY ./migration ./migration
COPY ./alembic.ini ./
# Указываем команду запуска
CMD ./start.sh
