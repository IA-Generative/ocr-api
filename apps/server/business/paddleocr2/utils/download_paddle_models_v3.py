import logging
from paddleocr import PaddleOCR
import clip
from business.paddleocr2.configs.paddle import PaddleSetting
from business.paddleocr2.configs.classification import ClassificationSettings
import os

settings = ClassificationSettings()


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def _maybe_dir(p: str, sub: str):
    if not p:
        return None
    d = os.path.join(p, sub)
    return d if os.path.exists(d) else None


det_dir = _maybe_dir(PaddleSetting().PADDLE_PDX_CACHE_HOME, "detection")
rec_dir = _maybe_dir(PaddleSetting().PADDLE_PDX_CACHE_HOME, "recognition")

if __name__ == "__main__":
    PaddleOCR(
        text_detection_model_dir=det_dir,
        text_recognition_model_dir=rec_dir,
        use_textline_orientation=False,
        use_doc_unwarping=False,
        lang="fr",
        ocr_version="PP-OCRv3",
    )
    clip.load(settings.MODEL_NAME, device="cpu", download_root=settings.CLIP_MODEL_DIR)
