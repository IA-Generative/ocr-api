FROM python:3.10-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt update -qy && apt install -qy poppler-utils && apt autoremove
ENV UV_CACHE_DIR=/app/.cache
ENV SURYA_DETECTION_FOLDER=/app/.cache/surya/detection
ENV SURYA_RECOGNITION_FOLDER=/app/.cache/surya/recognition

COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

RUN uv sync --no-cache --group ocr-service


COPY ocr_service /app/ocr_service
ENV PYTHONPATH=/app
RUN uv run /app/ocr_service/utils/download.py

COPY src /app/src

ENV MODEL_NAME=surya

CMD ["uv", "run", "ocr_service/main.py"]
