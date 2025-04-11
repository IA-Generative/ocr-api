import asyncio
import os
import time
from paddleocr import PaddleOCR
from pathlib import Path
import numpy as np

from ..logger import logger
from .fast_paddle import ppocr_v3, parse_paddle_ocr_result

# path_model = Path(os.getenv("MODEL_PATH", Path(__file__).parent.absolute()))

# OCRCustom = PaddleOCR(
#     det_model_dir=str(path_model / "detection"),
#     rec_model_dir=str(path_model / "recognition"),
#     cls_model_dir=str(path_model / "recognition"),
#     use_angle_cls=False,
#     lang="fr",
# )


async def perform_ocr_async(img_array: np.ndarray):
    t = time.time()
    logger.info(f"image shpe {img_array.shape}")
    if len(img_array.shape) == 4:
        result_ocr = await asyncio.to_thread(ppocr_v3.batch_predict, img_array)
        logger.debug(f"time to procces image : {time.time() - t}s")
        return [parse_paddle_ocr_result(res) for res in result_ocr]
    result_ocr = await asyncio.to_thread(ppocr_v3.predict, img_array)
    return [parse_paddle_ocr_result(result_ocr)]
