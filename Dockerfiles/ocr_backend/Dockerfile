FROM python:3.10-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

ENV UV_CACHE_DIR=/app/.cache
ENV FASTDEPLOY_HUB_HOME=/app/

COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

RUN uv sync --no-cache

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY ocr_backend /app/ocr_backend
COPY src /app/src

CMD ["uv", "run", "uvicorn", "ocr_backend.main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "2"]
