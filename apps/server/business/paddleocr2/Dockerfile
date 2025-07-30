FROM python:3.10-slim AS paddle_model
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt update -qy && apt install -qy ffmpeg libsm6 libxext6 curl poppler-utils && apt autoremove
ENV UV_CACHE_DIR=/app/.cache
ENV PADDLE_OCR_BASE_DIR=/app/.cache/paddle/

COPY apps/server/benchmark/paddle/2.10.0/pyproject.toml  /app/
RUN uv sync
ENV PYTHONPATH=/app
COPY apps/server/business/__init__.py /app/business/__init__.py
COPY apps/server/business/paddleocr2 /app/business/paddleocr2
RUN uv run /app/business/paddleocr2/utils/download_paddle_models.2.10.0.py --version PP-OCRv4 --folder $PADDLE_OCR_BASE_DIR

COPY apps/server/business/cache /app/business/cache
COPY apps/server/business/checkbox_service /app/business/checkbox_service
COPY apps/server/business/forms /app/business/forms

COPY apps/server/src /app/src
COPY apps/server/services /app/services/

ENV PATH=$PATH:/app/.venv/bin/

FROM paddle_model AS test
RUN uv add pytest pytest-asyncio coverage>=7.8.0 pytest-cov
