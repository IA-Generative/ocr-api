ARG HARBOR_PROXY_URL

FROM ${HARBOR_PROXY_URL:-docker.io}/python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt update -qy && apt install -qy \
  curl \
  ffmpeg \
  libsm6 \
  libxext6 \
  poppler-utils \
  && apt autoremove && rm -rf /var/lib/apt/lists/*
ENV UV_CACHE_DIR=/app/.cache
ENV PADDLE_OCR_BASE_DIR=/app/models/paddle/
ENV PADDLE_PDX_CACHE_HOME=/app/models/paddle/
ENV TORCH_HOME=/app/.cache/torch/
ENV HF_HOME=/app/.cache/huggingface/

COPY apps/server/pyproject.toml apps/server/uv.lock apps/server/.python-version  /app/
RUN uv sync --no-cache --group business-forms \
  --group checkbox_service \
  --group client \
  --group llm \
  --group ocr-service-paddle \
  --group ocr-docling \
  --group services \
  && uv cache clean

ENV PYTHONPATH=/app
# Download PaddleOCR models
COPY apps/server/business/paddleocr2 /app/business/paddleocr2
RUN uv run business/paddleocr2/utils/download_paddle_models_v3.py

# Copy application code
COPY apps/server/business/__init__.py /app/business/__init__.py
COPY apps/server/business/cache /app/business/cache
COPY apps/server/business/checkbox_service /app/business/checkbox_service
COPY apps/server/business/forms /app/business/forms
COPY apps/server/business/features /app/business/features
COPY apps/server/business/llm /app/business/llm
COPY apps/server/business/docling_inference /app/business/docling_inference
COPY apps/server/business/extractions /app/business/extractions
COPY apps/server/business/chunks /app/business/chunks

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
  --group ocr-docling \
  --group services \
  --group test \
  && uv cache clean
