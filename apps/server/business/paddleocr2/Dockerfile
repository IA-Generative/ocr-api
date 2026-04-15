ARG HARBOR_PROXY_URL

FROM ${HARBOR_PROXY_URL:-docker.io}/python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt update -qy && apt install -qy \
  curl \
  git \
  ffmpeg \
  libsm6 \
  libxext6 \
  poppler-utils \
  && apt autoremove && rm -rf /var/lib/apt/lists/*
ENV UV_CACHE_DIR=/app/.cache
ENV PADDLE_OCR_BASE_DIR=/app/models/paddle/
ENV PADDLE_PDX_CACHE_HOME=/app/models/paddle/
ENV TORCH_HOME=/app/models/torch/
ENV HF_HOME=/app/.cache/huggingface/
ENV TORCHINDUCTOR_CACHE_DIR=/tmp
ENV PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=true

COPY apps/server/pyproject.toml apps/server/uv.lock apps/server/.python-version  /app/
RUN uv sync --no-cache --group business-forms \
  --group checkbox_service \
  --group client \
  --group llm \
  --group ocr-service-paddle \
  --group ocr-service-features \
  --group services \
  && uv cache clean

ENV PYTHONPATH=/app
# Download PaddleOCR models
COPY apps/server/business /app/business/
RUN uv run business/paddleocr2/utils/download_paddle_models_v3.py
# RUN uv run business/classification/utils/dl_models.py

# Copy common code
COPY apps/server/src /app/src
COPY apps/server/services /app/services/
COPY apps/server/configs /app/configs/

ENV PATH=$PATH:/app/.venv/bin/


FROM builder AS test
RUN uv sync --no-cache --group business-forms \
  --group checkbox_service \
  --group client \
  --group llm \
  --group ocr-service-paddle \
  --group services \
  --group test \
  --group ocr-service-features \
  && uv cache clean
