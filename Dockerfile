FROM python:3.11-slim as base
WORKDIR /app

# librairies necessary for image processing
RUN apt update && apt install -y \
    ffmpeg libsm6 libxext6 curl poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# install python libraries
COPY requirements.txt .
RUN pip --default-timeout=300 install --upgrade pip \
    && pip --default-timeout=300 install --no-cache-dir -r requirements.txt \
    && rm -r /root/.cache

RUN mkdir -p /app/src/detection && mkdir -p /app/src/recognition
RUN curl -o det_infer.tar https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_infer.tar
RUN curl -o rec_infer.tar https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/latin_PP-OCRv3_rec_infer.tar
RUN tar xf det_infer.tar -C /app/src/detection --strip-components=1 \
    && tar xf rec_infer.tar -C /app/src/recognition --strip-components=1

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "3"]
