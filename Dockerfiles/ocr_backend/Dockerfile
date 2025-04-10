FROM python:3.10-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

ENV UV_CACHE_DIR=/app/.cache

COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

RUN uv sync --no-cache --group ocr-backend

COPY ocr_backend /app/ocr_backend
COPY src /app/src
COPY scripts /app/scripts
ENV PATH=$PATH:/app/.venv/bin/
ENV HOST 0.0.0.0
ENV PORT 5000
CMD ["./scripts/run.sh"]
