import time
from PIL import Image
from paddleocr import PaddleOCR
from pathlib import Path

model: PaddleOCR = PaddleOCR(ocr_version="PP-OCRv4", use_angle_cls=False, lang="fr", verbose=True)
total_time = 0
counter_image_pred = 0
for iter in range(10):
    images: list[Image.Image] = Path("/app/data").glob("*.png")
    for image in images:
        print(image)
        t = time.time()
        predictions = model.ocr(str(image), det=True, rec=True, cls=True)
        print(f"{image} - process in {time.time() - t}")
        total_time += time.time() - t
        counter_image_pred += 1
        print(f"avg time {total_time/counter_image_pred:.2f}s")
