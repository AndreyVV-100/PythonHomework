# Загрузка официального Docker-образа Python
FROM python:3.12-slim

# Установка рабочей директории
WORKDIR /app

# Установка переменных окружения.
# Отключение записи pyc-файлов на диск
ENV PYTHONDONTWRITEBYTECODE 1
# Отключение буферизации stdout и stderr
ENV PYTHONUNBUFFERED 1

# Установка библиотек
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копирование файлов проекта
COPY . .