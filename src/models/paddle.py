import asyncio
import os
import time
from paddleocr import PaddleOCR
from pathlib import Path

from ..logger import logger

path_model = Path(os.getenv("MODEL_PATH", Path(__file__).parent.absolute()))  

OCRCustom = PaddleOCR(
    det_model_dir=str(path_model / "detection"),
    rec_model_dir=str(path_model / "recognition"),
    cls_model_dir=str(path_model / "recognition"),
    use_angle_cls=False,
    lang="fr",
)


async def perform_ocr_async(img_array):
    t = time.time()
    result = await asyncio.to_thread(OCRCustom.ocr, img_array)
    logger.debug(f'time to procces image : {time.time() - t}s')
    return (
        [
            {
                "confidence": round(confidence, 2),
                "text": text,
                "text_region": [[int(x), int(y)] for x, y in bbox],
            }
            for bbox, (text, confidence) in result[0]
        ]
        if result != [None]
        else []
    )