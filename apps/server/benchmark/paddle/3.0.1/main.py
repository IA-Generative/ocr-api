import time
from PIL import Image
from paddleocr import PaddleOCR
from pathlib import Path

model: PaddleOCR = PaddleOCR(
    # text_detection_model_name=self.text_detection_model_name,
    # text_recognition_model_name=self.text_recognition_model_name,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    # use_textline_orientation
    ocr_version="PP-OCRv5",
    device="cpu",
    cpu_threads=8,
    # text_det_limit_side_len=960,
    # text_det_limit_type="max",
    # text_recognition_batch_size=12,
    enable_mkldnn=True,
    # text_det_limit_side_len=self.target_size,  # Synchroniser avec la taille de redimensionnement
    # text_det_limit_type="min",  # Redimensionner basé sur le côté le plus long
    # det_db_score_mode="fast",
    lang=None,
)


total_time = 0
counter_image_pred = 0
for iter in range(10):
    images: list[Image.Image] = Path("/app/data").glob("*.png")
    for image in images:
        print(image)
        t = time.time()
        predictions = model.predict(
            str(image),
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            # text_det_limit_side_len=960,
        )
        print(f"{image} - process in {time.time() - t}")
        total_time += time.time() - t
        counter_image_pred += 1
        print(f"avg time {total_time / counter_image_pred:.2f}s")
