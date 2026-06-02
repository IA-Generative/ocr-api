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
        logger.debug(
            f"[{self.__class__.__name__}] init parser_result is "
            f"{'set' if parser_result is not None else 'None'} "
            f"(pages={len(parser_result.pages) if parser_result else 0})"
        )

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

    def _fill_page_from_parser(self, page: Page) -> None:
        if not self.parser_result:
            return
        if page.page - 1 >= len(self.parser_result.pages):
            logger.warning(
                f"[{self.__class__.__name__}] image index {page.page} has no "
                f"matching parser page (parser pages={len(self.parser_result.pages)})"
            )
            return

        page_info = self.parser_result.pages[page.page]  # page.page is 1-based
        page_width = page_info.width or 0
        page_height = page_info.height or 0
        logger.debug(
            f"[{self.__class__.__name__}] page {page.page}: "
            f"{len(page_info.text_items)} text item(s) "
            f"(page size {page_width}x{page_height})"
        )
        if page_width <= 0 or page_height <= 0:
            logger.warning(
                f"[{self.__class__.__name__}] page {page.page} has invalid "
                f"dimensions ({page_width}x{page_height}); skipping normalization"
            )
            return
        for item in page_info.text_items:
            bbox = Bbox(
                text=item.text,
                x=item.x / page_width,
                y=item.y / page_height,
                width=item.width / page_width,
                height=item.height / page_height,
                confidence=(item.confidence if item.confidence is not None else 1.0),
            )
            page.boxes.append(bbox)

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

        if self.parser_result is None:
            logger.warning(
                f"[{self.__class__.__name__}] parser_result is None — no text "
                f"will be extracted for {len(images)} image(s)"
            )
        else:
            logger.info(
                f"[{self.__class__.__name__}] parser_result has "
                f"{len(self.parser_result.pages)} page(s) for {len(images)} image(s)"
            )

        logger.info(
            f"[{self.__class__.__name__}] Processing {len(images)} pages with parser result: {self.parser_result}"
        )
        for i, _ in enumerate(images):
            try:
                page = pages[i]
                self._fill_page_from_parser(page)
                result.append(page)
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Error processing file: {e}")
                page = Page(
                    page=i + 1,
                    boxes=[],
                )
                result.append(page)

        return result
