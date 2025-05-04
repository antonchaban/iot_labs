FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Встановлюємо робочу директорію
WORKDIR /usr/agent

# Копіюємо файл залежностей та встановлюємо залежності
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копіюємо увесь код додатку (включаючи папки src, schema, domain і т.п.)
COPY . .

# Створюємо директорію для CSV файлів, якщо її ще немає
RUN mkdir -p /usr/agent/data

# Копіюємо CSV файли з каталогу src/data у директорію data (відносно робочої теки)
RUN cp src/data/accelerometer.csv src/data/gps.csv /usr/agent/data/

# Якщо потрібне символічне посилання для lab1, можна його створити:
RUN ln -s /usr/agent /usr/agent/lab1

# Додаємо поточну директорію до шляху пошуку модулів Python
ENV PYTHONPATH=/usr/agent

# Запускаємо додаток через модуль, наприклад src.main
CMD ["python", "-m", "src.main"]
