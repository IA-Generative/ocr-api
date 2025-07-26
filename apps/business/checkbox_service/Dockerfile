FROM python:3.10-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

ARG SERVICE_NAME="checkbox_service"
ENV SERVICE_NAME=${SERVICE_NAME}


RUN apt-get update -qy && \
    apt-get install -qy --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
RUN uv sync --no-cache --group ${SERVICE_NAME} --group services

COPY ocr_backend /app/ocr_backend
COPY apps/src /app/src
COPY apps/services/ /app/services/
COPY apps/business/__init__.py /app/business/__init__.py
COPY apps/business/cache /app/business/cache
COPY apps/business/${SERVICE_NAME} /app/business/${SERVICE_NAME}

ENV PATH=$PATH:/app/.venv/bin/
ENV PYTHONPATH=/app/

FROM builder AS test
WORKDIR /app
COPY apps/tests tests
RUN uv sync --no-cache --group test --group ${SERVICE_NAME} --group services
