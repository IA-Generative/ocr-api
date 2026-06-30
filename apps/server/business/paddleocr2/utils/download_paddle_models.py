import argparse
import os


def parameters():
    parser = argparse.ArgumentParser(description="Choix de version et de folder.")
    parser.add_argument(
        "--version",
        required=False,
        default="PP-OCRv6",
        help="PaddleOCR model version (e.g. PP-OCRv4, PP-OCRv5, PP-OCRv6). "
        "Must match the version used at runtime in models/paddle.py.",
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

    from paddleocr import PaddleOCR

    print(f"Downloading PaddleOCR models into {os.environ.get('PADDLE_PDX_CACHE_HOME', '~/.paddlex')}...")
    PaddleOCR(
        use_doc_orientation_classify=True,
        use_doc_unwarping=False,
        use_textline_orientation=True,
        engine="paddle",
        lang="fr",
        ocr_version=args.version,
    )
