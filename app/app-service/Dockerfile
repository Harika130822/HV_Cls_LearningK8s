FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN adduser --disabled-password --gecos "" appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER appuser

EXPOSE 5002

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "2", "--threads", "4", "app_service:app"]
