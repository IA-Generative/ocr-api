FROM python:3.11-slim as base
WORKDIR /app

# librairies necessary for image processing
RUN apt update && apt install -y \
    ffmpeg libsm6 libxext6 curl \
    && rm -rf /var/lib/apt/lists/*

# install python libraries
COPY requirements.txt .
RUN pip --default-timeout=300 install --upgrade pip \
    && pip --default-timeout=300 install --no-cache-dir -r requirements.txt \
    && rm -r /root/.cache

RUN mkdir -p /app/models/detection && mkdir -p /app/models/recognition
RUN curl -o det_infer.tar https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_det_infer.tar
RUN curl -o rec_infer.tar https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/latin_PP-OCRv3_rec_infer.tar
RUN tar xf det_infer.tar -C /app/models/detection --strip-components=1 \
    && tar xf rec_infer.tar -C /app/models/recognition --strip-components=1

COPY . .

CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "5000"]