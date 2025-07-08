FROM python:3.10-slim AS llm_process
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt update -qy && apt install -qy ffmpeg libsm6 libxext6 curl poppler-utils && apt autoremove
ENV UV_CACHE_DIR=/app/.cache

COPY pyproject.toml uv.lock /app/

RUN uv sync --no-cache --group llm

RUN uv sync
ENV PYTHONPATH=/app
COPY business/__init__.py /app/business/__init__.py
COPY business/llm /app/business/llm
COPY business/checkbox_service /app/business/checkbox_service

COPY src /app/src
COPY services /app/services/

ENV PATH=$PATH:/app/.venv/bin/

FROM llm_process AS test
RUN uv add pytest pytest-asyncio coverage>=7.8.0 pytest-cov
