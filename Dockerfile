FROM python:3.10-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# librairies necessary for image processing
RUN apt update && apt install -y \
    ffmpeg libsm6 libxext6 curl poppler-utils \
    && rm -rf /var/lib/apt/lists/*

ENV DET_MODEL_DIR=/app/src/detection
ENV REC_MODEL_DIR=/app/src/recognition
ENV DET_MODEL_URL=https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_det_infer.tar
ENV REC_MODEL_URL=https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/latin_PP-OCRv3_rec_infer.tar
ENV UV_CACHE_DIR=/app/.cache
ENV FASTDEPLOY_HUB_HOME=/app/


RUN mkdir -p $DET_MODEL_DIR && mkdir -p $REC_MODEL_DIR
RUN curl -o det_infer.tar $DET_MODEL_URL
RUN curl -o rec_infer.tar $REC_MODEL_URL
RUN tar xf det_infer.tar -C $DET_MODEL_DIR --strip-components=1 \
    && tar xf rec_infer.tar -C $REC_MODEL_DIR --strip-components=1
RUN rm rec_infer.tar det_infer.tar

COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

RUN uv sync --no-cache

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY . .

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "2"]
