from io import BytesIO
from typing import List
from time import time
from PIL import Image

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream
from services.base.model import BaseModelPrediction

from src.schemas.output import Page
from src.schemas.box import Bbox
from src.logger import logger


class DoclingInferenceModel(BaseModelPrediction):
    def __init__(self):
        self.converter = DocumentConverter()

    def batch_predict(self, images: List[Image.Image], pages: list[Page] = [], *args, **kwargs) -> List[Page]:
        result: List[Page] = []
        if len(pages):
            assert len(images) == len(pages)

        for i, image in enumerate(images):
            logger.info(f"Processing image {i + 1}/{len(images)}")
            t = time()
            stream = DocumentStream(name=f"image-{i + 1}.png", stream=BytesIO(image.tobytes()))
            prediction_text = self.converter.convert(source=stream).document
            page_boxes: List[Bbox] = []

            box = Bbox(
                x=0,
                y=1,
                width=1,
                height=1,
                confidence=1.0,
                text=prediction_text.export_to_markdown(),
            )
            page_boxes.append(box)
            page = Page(page=i, boxes=page_boxes)
            result.append(page)
            logger.info(f"Image {i + 1} processed in {time() - t:.2f} seconds")

        return result
