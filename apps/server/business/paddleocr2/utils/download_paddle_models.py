import argparse
import os


def parameters():
    parser = argparse.ArgumentParser(description="Choix de version et de folder.")
    parser.add_argument(
        "--version",
        required=False,
        default=None,
        help="PaddleOCR model version (e.g. PP-OCRv3, PP-OCRv4). "
        "Defaults to PaddleSetting.OCR_VERSION if not specified.",
    )
    parser.add_argument(
        "--folder",
        required=False,
        default=None,
        help="Folder to download/cache the models into.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parameters()

    if args.folder:
        os.environ["PADDLE_PDX_CACHE_HOME"] = args.folder

    from business.paddleocr2.configs.paddle import PaddleSetting

    paddle_settings = PaddleSetting()
    version = args.version or paddle_settings.OCR_VERSION
    folder = args.folder or paddle_settings.PADDLE_OCR_BASE_DIR

    from paddleocr import PaddleOCR

    print(f"Downloading PaddleOCR {version} models into {folder}...")
    PaddleOCR(
        use_textline_orientation=False,
        use_doc_unwarping=False,
        lang="fr",
        ocr_version=version,
        device="cpu",
        cpu_threads=paddle_settings.CPU_THREADS,
        enable_mkldnn=paddle_settings.ENABLE_MKLDNN,
    )
