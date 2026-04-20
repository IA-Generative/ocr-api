#!/bin/bash
set -e

DATA_DIR="/data"
mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

echo "=== Downloading dataset ==="
wget -nc https://paddle-model-ecology.bj.bcebos.com/paddlex/data/ocr_rec_dataset_examples.tar
tar -xf ocr_rec_dataset_examples.tar

echo "=== Downloading PP-OCRv5_server_rec pretrained model ==="
wget -nc https://paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/PP-OCRv5_server_rec_pretrained.pdparams

echo "=== Done ==="
echo "Dataset:          $DATA_DIR/ocr_rec_dataset_examples"
echo "Pretrained model: $DATA_DIR/PP-OCRv5_server_rec_pretrained.pdparams"
