FROM python:3.13-alpine
LABEL authors="magomedov_sm"

WORKDIR /app
COPY ./requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта в рабочую директорию
COPY ./start.sh ./
COPY ./src ./src

# Указываем команду запуска
CMD ./start.sh
