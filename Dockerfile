# Базовый образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Указываем команду для запуска бота
CMD ["python3", "main.py"]
