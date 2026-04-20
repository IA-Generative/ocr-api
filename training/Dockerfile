ARG DOCKERHUB_MIRROR_URL

FROM ghcr.io/astral-sh/uv:latest AS uv_stage

FROM ${DOCKERHUB_MIRROR_URL:-ccr-2vdh3abv-pub.cnc.bj.baidubce.com}/paddlepaddle/paddle:3.0.0 AS builder

RUN git clone https://github.com/PaddlePaddle/PaddleOCR && \
  cd PaddleOCR && \
  git checkout eff5b7deda89e1829054535e6f6f53440355faa0

RUN python -m pip install paddleocr scikit-image pyyaml pynvml rapidfuzz lmdb


COPY training/*.sh /app/training/
RUN chmod +x /app/training/*.sh

ENV PYTHONPATH=/app:/app/PaddleOCR
ENV PATH=$PATH:/app/.venv/bin/

WORKDIR /app/training

