FROM python:3.12.3-slim

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y \
    gcc \
    cron \
    && rm -rf /var/lib/apt/lists/*

# env
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy toàn bộ project
COPY . .

# tạo thư mục database (nếu chưa có)
RUN mkdir -p /app/database /app/static/uploads

# 👉 COPY DB seed vào image
COPY database/app_data.db /app/database/app_data.db

CMD ["gunicorn", "main:app", "-c", "gunicorn.conf.py"]