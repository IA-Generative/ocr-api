import os
import argparse
from business.paddleocr2.configs.paddle import PaddleSetting
from paddleocr.paddleocr import get_model_config, MODEL_URLS, maybe_download


paddle_settings = PaddleSetting()


def parameters():
    parser = argparse.ArgumentParser(description="Choix de version et de folder.")
    AVAILABLE_VERSIONS = list(MODEL_URLS["STRUCTURE"].keys())
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
    table_url = get_model_config(type="STRUCTURE", version=args.version, model_type="table", lang="en")["url"]
    layout_url = get_model_config(type="STRUCTURE", version=args.version, model_type="layout", lang="en")["url"]
    formula_url = get_model_config(type="STRUCTURE", version=args.version, model_type="formula", lang="en")["url"]
    maybe_download(os.path.join(args.folder, "table"), table_url)
    maybe_download(os.path.join(args.folder, "layout"), layout_url)
    maybe_download(os.path.join(args.folder, "formula"), formula_url)
