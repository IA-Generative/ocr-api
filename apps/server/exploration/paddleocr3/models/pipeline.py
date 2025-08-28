from time import time

from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.logger import logger


class PipelineLinearPrediction(BaseModelPrediction):
    def __init__(self, models: list[BaseModelPrediction]):
        self.models = models

    def batch_predict(self, images, pages: list[Page] = [], *args, **kwargs) -> list[Page]:
        for model in self.models:
            t = time()
            pages = model.batch_predict(images=images, pages=pages)
            total_time = time() - t
            logger.debug(f"[{model.__class__.__name__}]: {total_time:.3f}s")
        return pages
