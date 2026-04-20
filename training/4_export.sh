#!/bin/bash
set -e

PADDLEOCR_DIR="/app/PaddleOCR"
CONFIG="configs/rec/PP-OCRv5/PP-OCRv5_server_rec.yml"
OUTPUT_DIR="/data/output/PP-OCRv5_server_rec"
INFER_DIR="/data/output/PP-OCRv5_server_rec_infer"

if [ ! -d "$PADDLEOCR_DIR" ]; then
  echo "ERROR: PaddleOCR not found at $PADDLEOCR_DIR"
  exit 1
fi

# Find latest checkpoint
WEIGHTS=$(ls -t "${OUTPUT_DIR}"/*.pdparams 2>/dev/null | head -1)
if [ -z "$WEIGHTS" ]; then
  echo "ERROR: No trained weights found in ${OUTPUT_DIR}"
  echo "Run 2_train.sh first."
  exit 1
fi

mkdir -p "$INFER_DIR"

echo "=== Exporting model from: $WEIGHTS ==="
echo "=== Output directory: $INFER_DIR ==="

TMP_CONFIG="/tmp/PP-OCRv5_server_rec_cpu.yml"
cp "$CONFIG" "$TMP_CONFIG"
sed -i 's/use_gpu: *true/use_gpu: false/I' "$TMP_CONFIG"

cd "$PADDLEOCR_DIR"

CUDA_VISIBLE_DEVICES="" python3 tools/export_model.py \
  -c "$TMP_CONFIG" \
  -o Global.use_gpu=False \
  -o Global.pretrained_model="${WEIGHTS%.pdparams}" \
  -o Global.save_inference_dir="$INFER_DIR"

echo "=== Export done ==="
echo "Static model saved to: $INFER_DIR"
ls "$INFER_DIR"
