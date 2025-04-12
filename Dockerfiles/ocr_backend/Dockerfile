FROM python:3.10-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

ENV UV_CACHE_DIR=/app/.cache

COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN uv sync --no-cache --group ocr-backend

COPY ocr_backend /app/ocr_backend
COPY src /app/src

CMD ["uv", "run", "uvicorn", "ocr_backend.main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "2"]
