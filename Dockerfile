FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/scripts

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --workers=1 --threads=8 --timeout=120"]
