# Используем официальный образ Python
FROM python:latest

# Устанавливаем рабочую директорию
WORKDIR /bread_ordering

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости, если есть requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Указываем команду для запуска приложения
CMD ["python", "bread_ordering/manage.py", "runserver", "0.0.0.0:8000"]