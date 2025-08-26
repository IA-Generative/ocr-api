import os


def download_model(folder: str, version: str = "PP-OCRv4"):
    from paddleocr.paddleocr import get_model_config, maybe_download

    det_url = get_model_config(type="OCR", version=version, model_type="det", lang="en")["url"]
    rec_url = get_model_config(type="OCR", version=version, model_type="rec", lang="latin")["url"]
    cls_url = get_model_config(type="OCR", version=version, model_type="cls", lang="ch")["url"]
    maybe_download(os.path.join(folder, "DETECTION_FOLDER"), det_url)
    maybe_download(os.path.join(folder, "RECOGNITION_FOLDER"), rec_url)
    maybe_download(os.path.join(folder, "CLASSIFICATION_FOLDER"), cls_url)
