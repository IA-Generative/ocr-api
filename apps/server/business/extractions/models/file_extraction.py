from typing import Union

from src.schemas.output import Page, Bbox
from src.schemas.task import TaskModel
from src.logger import logger
from liteparse.types import ParseResult
from business.extractions.models.inference import FileExtractionModel
from PIL import Image
from .content_types import (
    ODT_CONTENT_TYPE,
    ODS_CONTENT_TYPE,
    ODP_CONTENT_TYPE,
    DOCX_CONTENT_TYPE,
    EXCEL_CONTENT_TYPE,
    CSV_CONTENT_TYPE,
)


class FileHandlerExtractionModel(FileExtractionModel):
    def __init__(self, parser_result: ParseResult | None = None):
        self.parser_result = parser_result

    def is_applicable(self, task: TaskModel) -> bool:
        if not task.input or not task.input.content_type:
            return False
        return (
            task.input.content_type
            in ODT_CONTENT_TYPE
            + ODS_CONTENT_TYPE
            + ODP_CONTENT_TYPE
            + DOCX_CONTENT_TYPE
            + EXCEL_CONTENT_TYPE
            + CSV_CONTENT_TYPE
        )

    def batch_predict(
        self,
        images: list[Union[bytes, str, Image.Image]],
        pages: list[Page] | None = None,
        *args,
        **kwargs,
    ) -> list[Page]:
        result: list[Page] = []
        if pages is not None and len(pages) != len(images):
            logger.warning(
                f"[{self.__class__.__name__}] Number of pages provided ({len(pages)}) does not match number of images ({len(images)}). Ignoring provided pages."
            )
            raise ValueError("Number of pages must match number of images")
        if pages is None:
            pages = [Page(page=i + 1, boxes=[]) for i in range(len(images))]

        for i, _ in enumerate(images):
            try:
                page = pages[i]
                if self.parser_result and i < len(self.parser_result.pages):
                    page_info = self.parser_result.pages[i]

                    for item in page_info.text_items:
                        bbox = Bbox(
                            text=item.text,
                            x=item.x,
                            y=item.y,
                            width=item.width,
                            height=item.height,
                            confidence=(item.confidence if item.confidence is not None else 1.0),
                        )
                        page.boxes.append(bbox)

                result.append(page)
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Error processing file: {e}")
                page = Page(
                    page=i + 1,
                    boxes=[],
                )
                result.append(page)

        return result
