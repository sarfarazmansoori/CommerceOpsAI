FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --default-timeout=180 --retries=10 -r requirements.txt \
    && groupadd --system appgroup \
    && useradd --system --gid appgroup appuser \
    && mkdir -p /app/logs \
    && chown -R appuser:appgroup /app

COPY --chown=appuser:appgroup src/ ./src/

USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
