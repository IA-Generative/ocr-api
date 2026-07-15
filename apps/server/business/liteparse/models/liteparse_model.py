import os
from io import BytesIO
from typing import Optional, Union
from uuid import uuid4

from services.base.model import BaseModelPrediction
from src.schemas.output import Page, Bbox
from src.schemas.task import TaskModel
from src.logger import logger

try:
    from liteparse import LiteParse
except ImportError:
    LiteParse = None  # type: ignore[assignment,misc]

LITEPARSE_CONTENT_TYPES = [
    # CSV / TSV
    "text/csv",
    "text/tab-separated-values",
    # DOCX / DOC / DOCM
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-word.document.macroEnabled.12",
    "application/docx",
    "application/msword",
    "application/x-docx",
    "application/doc",
    "application/ms-doc",
    # RTF
    "text/rtf",
    "application/rtf",
    # Apple Pages
    "application/vnd.apple.pages",
    # XLSX / XLS / XLSM
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel.sheet.macroEnabled.12",
    "application/vnd.ms-excel",
    "application/xlsx",
    "application/xls",
    "application/x-xlsx",
    "application/x-xls",
    "application/x-excel",
    "application/x-msexcel",
    # Apple Numbers
    "application/vnd.apple.numbers",
    # PPTX / PPT / PPTM
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.ms-powerpoint.presentation.macroEnabled.12",
    "application/vnd.ms-powerpoint",
    # Apple Keynote
    "application/vnd.apple.keynote",
    # OpenDocument
    "application/vnd.oasis.opendocument.text",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.oasis.opendocument.presentation",
]


def parsed_page_to_schema(lp_page, page_url: Optional[str] = None) -> Page:
    """Convertit une ``ParsedPage`` liteparse en ``Page`` (bboxes déjà en texte, pas d'OCR)."""
    page_width = lp_page.width or 1
    page_height = lp_page.height or 1

    boxes: list[Bbox] = [
        Bbox(
            x=item.x / page_width,
            y=item.y / page_height,
            width=item.width / page_width,
            height=item.height / page_height,
            text=item.text,
            confidence=(item.confidence if item.confidence is not None else 1.0),
        )
        for item in (lp_page.text_items or [])
        if item.text.strip()
    ]

    # Fallback: one full-page bbox with the markdown text if no text_items
    if not boxes and lp_page.markdown:
        boxes = [
            Bbox(
                x=0,
                y=0,
                width=1,
                height=1,
                text=lp_page.markdown,
                confidence=1.0,
            )
        ]

    return Page(page=lp_page.page_num, page_url=page_url, boxes=boxes)


_CONTENT_TYPE_TO_EXT: dict[str, str] = {
    "text/csv": ".csv",
    "text/tab-separated-values": ".tsv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-word.document.macroEnabled.12": ".docm",
    "application/docx": ".docx",
    "application/msword": ".doc",
    "application/x-docx": ".docx",
    "application/doc": ".doc",
    "application/ms-doc": ".doc",
    "text/rtf": ".rtf",
    "application/rtf": ".rtf",
    "application/vnd.apple.pages": ".pages",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.ms-excel.sheet.macroEnabled.12": ".xlsm",
    "application/vnd.ms-excel": ".xls",
    "application/xlsx": ".xlsx",
    "application/xls": ".xls",
    "application/x-xlsx": ".xlsx",
    "application/x-xls": ".xls",
    "application/x-excel": ".xls",
    "application/x-msexcel": ".xls",
    "application/vnd.apple.numbers": ".numbers",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/vnd.ms-powerpoint.presentation.macroEnabled.12": ".pptm",
    "application/vnd.ms-powerpoint": ".ppt",
    "application/vnd.apple.keynote": ".key",
    "application/vnd.oasis.opendocument.text": ".odt",
    "application/vnd.oasis.opendocument.spreadsheet": ".ods",
    "application/vnd.oasis.opendocument.presentation": ".odp",
}


class LiteparseExtractionModel(BaseModelPrediction):
    def __init__(self, file_connector=None):
        if LiteParse is None:
            raise ImportError("liteparse is not installed. Run: pip install liteparse")

        self._parser = LiteParse(
            ocr_enabled=False,
            output_format="markdown",
            image_mode="off",
            quiet=True,
        )
        self._file_connector = file_connector

    def is_applicable(self, task: TaskModel) -> bool:
        return task.input.content_type in LITEPARSE_CONTENT_TYPES

    def _resolve_extension(self, task: TaskModel) -> str:
        if task.input.ext:
            return task.input.ext
        _, ext = os.path.splitext(task.input.raw_filename)
        if ext:
            return ext
        return _CONTENT_TYPE_TO_EXT.get(task.input.content_type, "")

    def batch_predict(
        self,
        images: list[Union[bytes, str]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        result: list[Page] = []
        task: Optional[TaskModel] = self.current_task
        ext = self._resolve_extension(task) if task else ""

        for i, raw_bytes in enumerate(images):
            temp_path = f"/tmp/liteparse_{uuid4()}{ext}"
            try:
                with open(temp_path, "wb") as f:
                    f.write(raw_bytes)

                liteparse_result = self._parser.parse(temp_path)
                lp_pages = liteparse_result.pages or []
                logger.info(
                    f"[LiteparseExtractionModel] file={task.input.raw_filename if task else '?'} "
                    f"pages_liteparse={len(lp_pages)}"
                )

                # Build a page_num → S3 key map for all pages (pas de presigned url
                # ici : elle est générée à la demande via la route /tasks/{id}/pages/{n}/url).
                screenshot_urls: dict[int, str] = {}
                if self._file_connector and task:
                    try:
                        client_s3 = self._file_connector.client
                        bucket = self._file_connector.bucket_name
                        for s in self._parser.screenshot(temp_path):
                            key = f"{task.user_id}/{task.id}/images/page_{s.page_num}.png"
                            client_s3.upload_fileobj(BytesIO(s.image_bytes), bucket, key)
                            screenshot_urls[s.page_num] = key
                            logger.info(f"[LiteparseExtractionModel] Screenshot saved: {key}")
                    except Exception as screenshot_err:
                        logger.warning(f"[LiteparseExtractionModel] Screenshots failed: {screenshot_err}")

                # One Page per liteparse page with real bboxes and screenshot
                for lp_page in lp_pages:
                    result.append(parsed_page_to_schema(lp_page, page_url=screenshot_urls.get(lp_page.page_num)))

                # Fallback: if liteparse returned no pages, keep the full text in one page
                if not lp_pages:
                    result.append(
                        Page(
                            page=1,
                            page_url=screenshot_urls.get(1),
                            boxes=[
                                Bbox(
                                    x=0,
                                    y=0,
                                    width=1,
                                    height=1,
                                    text=liteparse_result.text or "",
                                    confidence=1.0,
                                )
                            ],
                        )
                    )

            except Exception as e:
                logger.error(f"[LiteparseExtractionModel] Error processing file (page {i + 1}): {e}")
                result.append(Page(page=i + 1, boxes=[]))
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        return result
