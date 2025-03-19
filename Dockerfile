FROM python:3.11-slim as base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# librairies necessary for image processing
RUN apt update && apt install -y \
    ffmpeg libsm6 libxext6 curl poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# install python libraries
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock


RUN mkdir -p /app/models/detection && mkdir -p /app/models/recognition
RUN curl -o det_infer.tar https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_det_infer.tar
RUN curl -o rec_infer.tar https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/latin_PP-OCRv3_rec_infer.tar
RUN tar xf det_infer.tar -C /app/models/detection --strip-components=1 \
    && tar xf rec_infer.tar -C /app/models/recognition --strip-components=1

RUN uv sync \
    && rm -r /root/.cache

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]
