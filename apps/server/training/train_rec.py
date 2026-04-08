"""Fine-tune a PaddleOCR text-recognition model.

Uses tools/train.py from the PaddleOCR source repo (cloned automatically if absent).

Dataset format expected in --dataset_dir:
  <dataset_dir>/
    train.txt   # lines: relative/path/to/image.jpg\tlabel
    val.txt     # same format
    dict.txt    # one character per line (label vocabulary)
    images/     # images referenced by train.txt / val.txt

Usage examples:
  uv run training/train_rec.py --dataset_dir data/funsd_recognition/

  uv run training/train_rec.py \\
      --model PP-OCRv5_server_rec \\
      --dataset_dir /data/my_dataset \\
      --output ./output/pp_ocrv5 \\
      --epochs 50 --batch_size 64 --lr 0.001 --device gpu:0
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Model → config file (relative to PaddleOCR source root)
# ---------------------------------------------------------------------------
MODEL_CONFIGS: dict[str, str] = {
    "PP-OCRv5_server_rec": "configs/rec/PP-OCRv5/PP-OCRv5_server_rec.yml",
    "PP-OCRv5_mobile_rec": "configs/rec/PP-OCRv5/PP-OCRv5_mobile_rec.yml",
    "PP-OCRv4_server_rec": "configs/rec/PP-OCRv4/ch_PP-OCRv4_rec.yml",
    "PP-OCRv4_mobile_rec": "configs/rec/PP-OCRv4/ch_PP-OCRv4_rec_distillation.yml",
    "en_PP-OCRv4_mobile_rec": "configs/rec/PP-OCRv4/en_PP-OCRv4_mobile_rec.yml",
    "PP-OCRv3_mobile_rec": "configs/rec/PP-OCRv3/PP-OCRv3_mobile_rec.yml",
}

# Pretrained weights download URLs
PRETRAINED_URLS: dict[str, str] = {
    "PP-OCRv5_server_rec": "https://paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/PP-OCRv5_server_rec_pretrained.pdparams",
    "PP-OCRv5_mobile_rec": "https://paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/PP-OCRv5_mobile_rec_pretrained.pdparams",
    "PP-OCRv4_server_rec": "https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/PP-OCRv4_server_rec_pretrained.pdparams",
    "PP-OCRv4_mobile_rec": "https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/PP-OCRv4_mobile_rec_pretrained.pdparams",
}

PADDLEOCR_REPO = "https://github.com/PaddlePaddle/PaddleOCR.git"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fine-tune a PaddleOCR text-recognition model.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--dataset_dir", required=True, help="Dir with train.txt, val.txt, dict.txt.")
    parser.add_argument("--model", default="PP-OCRv3_mobile_rec", choices=list(MODEL_CONFIGS))
    parser.add_argument("--output", default="training/output/rec", help="Checkpoint output dir.")
    parser.add_argument("--pretrain_weight", default=None, help="Local .pdparams checkpoint.")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=0.0005)
    parser.add_argument("--device", default="cpu", help="'cpu', 'gpu', 'gpu:0', 'gpu:0,1' …")
    parser.add_argument("--log_interval", type=int, default=1, help="Print metrics every N steps.")
    parser.add_argument("--gpus", default=None, help="GPU IDs for multi-GPU, e.g. '0,1,2,3'.")
    parser.add_argument("--paddleocr_dir", default=None, help="Local PaddleOCR source path.")
    parser.add_argument(
        "--smoke_test",
        action="store_true",
        help="Quick sanity check: 1 epoch, batch 1, 5 samples — just verifies the pipeline runs.",
    )
    return parser.parse_args()


def ensure_source(paddleocr_dir: str | None) -> Path:
    path = Path(paddleocr_dir) if paddleocr_dir else Path("PaddleOCR")
    if not (path / "tools" / "train.py").exists():
        print(f"[INFO] Cloning PaddleOCR into {path} …")
        subprocess.check_call(["git", "clone", "--depth", "1", PADDLEOCR_REPO, str(path)])
    return path.resolve()


def download_pretrain(model: str, dest_dir: Path) -> Path | None:
    url = PRETRAINED_URLS.get(model)
    if not url:
        return None
    dest = dest_dir / f"{model}_pretrained.pdparams"
    if not dest.exists():
        print(f"[INFO] Downloading pretrained weights for {model} …")
        subprocess.check_call(["wget", "-q", "-O", str(dest), url])
    return dest


def validate_dataset(d: str) -> None:
    missing = [f for f in ["train.txt", "val.txt", "dict.txt"] if not os.path.isfile(f"{d}/{f}")]
    if missing:
        print(f"[ERROR] Missing in {d}: {', '.join(missing)}")
        sys.exit(1)


def write_smoke_files(dataset: str, tmp_dir: Path) -> tuple[Path, Path]:
    """Write train_smoke.txt / val_smoke.txt with 5 lines each."""
    for split in ("train", "val"):
        src = Path(dataset) / f"{split}.txt"
        dst = tmp_dir / f"{split}_smoke.txt"
        with open(src) as f:
            lines = [sample for sample in f if sample.strip()][:5]
        dst.write_text("".join(lines))
    return tmp_dir / "train_smoke.txt", tmp_dir / "val_smoke.txt"


def main() -> None:
    args = parse_args()
    validate_dataset(args.dataset_dir)

    repo = ensure_source(args.paddleocr_dir)
    config_path = repo / MODEL_CONFIGS[args.model]
    if not config_path.exists():
        print(f"[ERROR] Config not found: {config_path}")
        sys.exit(1)

    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)

    # Smoke-test: override settings before doing anything expensive
    if args.smoke_test:
        print("[SMOKE TEST] 1 epoch · batch 1 · 5 samples — verifying pipeline …")
        args.epochs = 1
        args.batch_size = 1
        args.lr = 0.0005
        train_file, val_file = write_smoke_files(os.path.abspath(args.dataset_dir), out)
    else:
        train_file = Path(os.path.abspath(args.dataset_dir)) / "train.txt"
        val_file = Path(os.path.abspath(args.dataset_dir)) / "val.txt"

    pretrain = None if args.smoke_test else download_pretrain(args.model, out)
    if args.pretrain_weight:
        pretrain = Path(args.pretrain_weight).resolve()

    dataset = os.path.abspath(args.dataset_dir)
    use_gpu = "false" if args.device == "cpu" else "true"

    overrides = [
        f"Global.epoch_num={args.epochs}",
        f"Global.save_model_dir={out}",
        f"Global.use_gpu={use_gpu}",
        f"Global.character_dict_path={dataset}/dict.txt",
        f"Global.print_batch_step={args.log_interval}",
        f"Global.log_smooth_window={args.log_interval}",
        "Global.cal_metric_during_train=true",
        f"Train.loader.batch_size_per_card={args.batch_size}",
        f"Eval.loader.batch_size_per_card={args.batch_size}",
        f"Optimizer.lr.learning_rate={args.lr}",
        f"Train.dataset.data_dir={dataset}",
        f"Train.dataset.label_file_list=[{train_file}]",
        f"Eval.dataset.data_dir={dataset}",
        f"Eval.dataset.label_file_list=[{val_file}]",
    ]
    if pretrain:
        overrides.append(f"Global.pretrained_model={pretrain}")

    print("─" * 55)
    print("  PaddleOCR Recognition — Fine-tuning")
    print("─" * 55)
    print(f"  Model     : {args.model}")
    print(f"  Config    : {config_path}")
    print(f"  Dataset   : {dataset}")
    print(f"  Output    : {out}")
    print(f"  Epochs    : {args.epochs}  |  Batch: {args.batch_size}  |  LR: {args.lr}")
    print(f"  Device    : {args.device}")
    if pretrain:
        print(f"  Pretrain  : {pretrain}")
    print("─" * 55)

    if args.gpus:
        cmd = [
            sys.executable,
            "-m",
            "paddle.distributed.launch",
            "--gpus",
            args.gpus,
            str(repo / "tools" / "train.py"),
            "-c",
            str(config_path),
            "-o",
            *overrides,
        ]
    else:
        cmd = [
            sys.executable,
            str(repo / "tools" / "train.py"),
            "-c",
            str(config_path),
            "-o",
            *overrides,
        ]

    print(f"[CMD] {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(repo))
    if result.returncode != 0:
        sys.exit(result.returncode)

    # -------------------------------------------------------------------
    # Export the trained model to inference format
    # -------------------------------------------------------------------
    # Skip export+eval with fine-tuned weights in smoke_test mode: 1 epoch on
    # 5 samples would severely degrade the model quality.  We still run eval
    # to verify the pipeline end-to-end, but against the default pretrained model.
    rec_model_dir_arg: list[str] = []
    if args.smoke_test:
        print("\n[INFO] Smoke-test : export ignoré — l'évaluation utilisera le modèle pré-entraîné par défaut.")
    else:
        export_out = out / "inference"
        export_tools = repo / "tools" / "export_model.py"
        if export_tools.exists():
            print("\n" + "─" * 55)
            print("  Export du modèle en format inférence")
            print("─" * 55)
            config_path = out / "config.yml"
            export_cmd = [
                sys.executable,
                str(export_tools),
                "-c",
                str(config_path),
                "-o",
                f"Global.pretrained_model={out / 'latest'}",
                f"Global.save_inference_dir={export_out}",
            ]
            export_result = subprocess.run(export_cmd, cwd=str(repo))
            if export_result.returncode != 0:
                print("[WARN] Export du modèle échoué — l'évaluation utilisera le modèle par défaut.")
            else:
                rec_model_dir_arg = ["--rec_model_dir", str(export_out)]
        else:
            print("[WARN] tools/export_model.py introuvable — l'évaluation utilisera le modèle par défaut.")

    # -------------------------------------------------------------------
    # Post-training evaluation via evaluations.py
    # -------------------------------------------------------------------
    print("\n" + "─" * 55)
    print("  Évaluation post-entraînement")
    print("─" * 55)
    eval_script = Path(__file__).parent / "evaluations.py"
    eval_cmd = [sys.executable, str(eval_script), *rec_model_dir_arg]
    eval_result = subprocess.run(eval_cmd, cwd=str(Path(__file__).parent))
    sys.exit(eval_result.returncode)


if __name__ == "__main__":
    main()
