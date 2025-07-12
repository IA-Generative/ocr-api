FROM paddlepaddle/paddle:3.0.0 AS paddle_model
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive

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

ENV MKLDNN_VERBOSE=1
ENV UV_CACHE_DIR=/app/.cache
ENV PADDLE_OCR_BASE_DIR=/app/.cache/paddle/
ENV PADDLE_PDX_CACHE_HOME=/app/.tmp/paddlex/
ARG PADDLE_OCR_VERSION="PP-OCRv4"
ENV PADDLE_OCR_VERSION=${PADDLE_OCR_VERSION}

WORKDIR /app

COPY pyproject.toml uv.lock /app/

RUN uv sync --no-cache --group ocr-service-paddle --group llm

ENV PYTHONPATH=/app
COPY services /app/services
COPY src /app/src
COPY business/__init__.py /app/business/__init__.py
COPY business/paddleocr3 /app/business/paddleocr3
COPY business/llm /app/business/llm
COPY business/checkbox_service /app/business/checkbox_service

RUN uv run /app/business/paddleocr3/utils/download_paddle_models.py
ENV PATH=$PATH:/app/.venv/bin/
CMD ["uv", "run", "services/main.py"]

FROM paddle_model AS test
RUN uv sync --group test --group ocr-service-paddle --group llm
COPY tests /app/tests
CMD ["uv", "run", "services/main.py"]
