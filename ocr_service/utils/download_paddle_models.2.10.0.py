import os
import argparse
from ocr_service.configs.paddle import PaddleSetting
from paddleocr.paddleocr import get_model_config, MODEL_URLS, maybe_download


paddle_settings = PaddleSetting()


def parameters():
    parser = argparse.ArgumentParser(description="Choix de version et de folder.")
    AVAILABLE_VERSIONS = list(MODEL_URLS["OCR"].keys())
    parser.add_argument(
        "--version",
        choices=AVAILABLE_VERSIONS,
        required=True,
        help=f"PaddleOcr model version choice ({AVAILABLE_VERSIONS}).",
    )

    parser.add_argument(
        "--folder",
        required=False,
        default=paddle_settings.PADDLE_OCR_BASE_DIR,
        help="folder to save models.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parameters()
    # TODO: add possibility to get language
    det_url = get_model_config(type="OCR", version=args.version, model_type="det", lang="en")["url"]
    rec_url = get_model_config(type="OCR", version=args.version, model_type="rec", lang="latin")["url"]
    cls_url = get_model_config(type="OCR", version=args.version, model_type="cls", lang="ch")["url"]
    maybe_download(os.path.join(args.folder, paddle_settings.DETECTION_FOLDER), det_url)
    maybe_download(os.path.join(args.folder, paddle_settings.RECOGNITION_FOLDER), rec_url)
    maybe_download(os.path.join(args.folder, paddle_settings.CLASSIFICATION_FOLDER), cls_url)
