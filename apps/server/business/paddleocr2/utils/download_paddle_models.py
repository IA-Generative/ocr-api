import argparse
import os


def parameters():
    parser = argparse.ArgumentParser(description="Choix de version et de folder.")
    parser.add_argument(
        "--version",
        required=False,
        default="PP-OCRv5",
        help="PaddleOCR model version (e.g. PP-OCRv4, PP-OCRv5). "
        "PPStructureV3 doesn't support PP-OCRv6 yet. "
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

    from paddleocr import PPStructureV3

    print(f"Downloading PaddleOCR models into {os.environ.get('PADDLE_PDX_CACHE_HOME', '~/.paddlex')}...")
    # Must match models/paddle.py:PaddleInferOCR2 constructor params so the
    # right models are pre-downloaded.
    PPStructureV3(
        use_doc_orientation_classify=True,
        use_doc_unwarping=False,
        use_textline_orientation=True,
        use_table_recognition=True,
        use_formula_recognition=False,
        use_chart_recognition=False,
        use_seal_recognition=False,
        lang="fr",
        ocr_version=args.version,
    )
