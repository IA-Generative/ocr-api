from typing import Union

from PIL import Image

from src.schemas.output import Page, Bbox
from src.schemas.task import TaskModel
from src.logger import logger
from services.base.model import BaseModelPrediction
from business.extractions.models.inference import FileExtractionModel
from business.extractions.models.content_types import EMAIL_CONTENT_TYPE


class EmailExtractionModel(FileExtractionModel):
    """
    Modèle d'extraction hybride pour les emails.

    Chaque page composite (email + pièces jointes) est traitée selon sa source :
      - page bureautique (ODT, DOCX, ...) : le texte a déjà été extrait par
        liteparse, on réutilise les ``text_items`` (aucun OCR) ;
      - page PDF ou image : on applique l'OCR Paddle.

    ``page_sources`` et ``ocr_pages`` sont fournis par ``LazyEmailList`` et
    posés par ``EmailWorker.transform_content``.
    """

    def __init__(self, ocr_model: BaseModelPrediction):
        self.ocr_model = ocr_model
        self.current_task: TaskModel | None = None
        # page_sources[i] = ParsedPage (texte liteparse) ou None (à OCR-iser)
        self.page_sources: list = []
        self.ocr_pages: set[int] = set()

    def is_applicable(self, task: TaskModel) -> bool:
        if not task.input or not task.input.content_type:
            return False
        return task.input.content_type in EMAIL_CONTENT_TYPE

    def set_current_task(self, task: TaskModel):
        super().set_current_task(task)
        self.ocr_model.set_current_task(task)

    def _fill_from_parser(self, page: Page, parsed) -> None:
        page_width = getattr(parsed, "width", 0) or 0
        page_height = getattr(parsed, "height", 0) or 0
        if page_width <= 0 or page_height <= 0:
            logger.warning(
                f"[{self.__class__.__name__}] page {page.page} has invalid "
                f"dimensions ({page_width}x{page_height}); skipping"
            )
            return
        for item in parsed.text_items:
            page.boxes.append(
                Bbox(
                    text=item.text,
                    x=item.x / page_width,
                    y=item.y / page_height,
                    width=item.width / page_width,
                    height=item.height / page_height,
                    confidence=(item.confidence if item.confidence is not None else 1.0),
                )
            )

    def _ocr_page(self, image: Union[bytes, str, Image.Image], page: Page) -> Page:
        ocr_result = self.ocr_model.batch_predict(
            images=[image],  # ty:ignore[invalid-argument-type]
            pages=[Page(page=page.page, boxes=[])],
        )
        filled = ocr_result[0]
        filled.page = page.page
        return filled

    def batch_predict(
        self,
        images: list[Union[bytes, str, Image.Image]],
        pages: list[Page] | None = None,
        *args,
        **kwargs,
    ) -> list[Page]:
        if pages is None:
            pages = [Page(page=i, boxes=[]) for i in range(len(images))]
        if len(pages) != len(images):
            raise ValueError("Number of pages must match number of images")

        result: list[Page] = []
        for image, page in zip(images, pages):
            index = page.page  # index global 0-based
            try:
                if index in self.ocr_pages:
                    logger.debug(f"[{self.__class__.__name__}] page {index} -> OCR Paddle")
                    result.append(self._ocr_page(image, page))
                else:
                    parsed = self.page_sources[index] if index < len(self.page_sources) else None
                    if parsed is not None:
                        logger.debug(f"[{self.__class__.__name__}] page {index} -> texte liteparse")
                        self._fill_from_parser(page, parsed)
                    result.append(page)
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Error processing page {index}: {e}")
                result.append(Page(page=index, boxes=[]))
        return result
