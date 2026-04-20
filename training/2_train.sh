#!/bin/bash
set -e

PADDLEOCR_DIR="/home/PaddleOCR"
CONFIG="configs/rec/PP-OCRv5/PP-OCRv5_server_rec.yml"
PRETRAINED_MODEL="/data/PP-OCRv5_server_rec_pretrained.pdparams"
TRAIN_LIST="/data/ocr_rec_dataset_examples/train.txt"
EVAL_LIST="/data/ocr_rec_dataset_examples/val.txt"
OUTPUT_DIR="/data/output/PP-OCRv5_server_rec"

if [ ! -d "$PADDLEOCR_DIR" ]; then
  echo "ERROR: PaddleOCR not found at $PADDLEOCR_DIR"
  exit 1
fi

if [ ! -f "$PRETRAINED_MODEL" ]; then
  echo "ERROR: Pretrained model not found at $PRETRAINED_MODEL"
  echo "Run 1_download_dataset.sh first."
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
cd "$PADDLEOCR_DIR"

# Patch the config to force CPU and set dataset paths
TMP_CONFIG="/tmp/PP-OCRv5_server_rec_cpu.yml"
cp "${PADDLEOCR_DIR}/${CONFIG}" "$TMP_CONFIG"
sed -i 's/use_gpu: *true/use_gpu: false/I' "$TMP_CONFIG"
sed -i "s|pretrained_model:.*|pretrained_model: ${PRETRAINED_MODEL}|" "$TMP_CONFIG"
sed -i "s|save_model_dir:.*|save_model_dir: ${OUTPUT_DIR}|" "$TMP_CONFIG"
# Replace train label file list
python3 -c "
import yaml, sys
with open('$TMP_CONFIG') as f:
    cfg = yaml.safe_load(f)
cfg['Train']['dataset']['label_file_list'] = ['$TRAIN_LIST']
cfg['Train']['dataset']['data_dir'] = '/data/ocr_rec_dataset_examples/'
cfg['Eval']['dataset']['label_file_list'] = ['$EVAL_LIST']
cfg['Eval']['dataset']['data_dir'] = '/data/ocr_rec_dataset_examples/'
with open('$TMP_CONFIG', 'w') as f:
    yaml.dump(cfg, f, allow_unicode=True)
"

echo "=== Starting training (CPU) ==="
CUDA_VISIBLE_DEVICES="" python3 tools/train.py -c "$TMP_CONFIG"

echo "=== Training done. Weights saved to $OUTPUT_DIR ==="
