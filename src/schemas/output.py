from typing import List, Optional, Any

from PIL import Image
from pydantic import BaseModel, ConfigDict

from src.schemas.box import Bbox
from src.utils.bboxes import get_text_from_list_bboxes, sort_bboxes_reading_order


class Page(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    page: int
    page_url: Optional[str] = None
    boxes: List[Bbox]

class MarkdownPageWithBBox(Page):
    model_config = ConfigDict(from_attributes=True)
    page: int
    doc_json: str
    markdown: str

class DoclingPage(BaseModel):
    page_no: int # Attention: page_no commence à 1
    boxes: List[Bbox]
    pil_image: Optional[Any] # Image.Image
    page_url: Optional[str] = None

class DoclingDocument(BaseModel):
    doc_json: str
    markdown: str
    pages: list[DoclingPage]


class OCRResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str
    model_name: str
    created_at: int
    updated_at: int
    version: str
    total_pages: int
    pages: List[Page | DoclingDocument]
    extras: Optional[dict] = None
    text: Optional[str] = ""

    def set_text(self, delta_y: float = 0.005):
        self.text = ""
        pages_content_per_page = []

        for i, page in enumerate(self.pages):
            page_lines_content = [f"{20*'-'} Page: {i+1} {20*'-'}"]

            sorted_bboxes = sort_bboxes_reading_order(
                bboxes=page.boxes, delta_y=delta_y
            )
            for line_sorted_boxes in sorted_bboxes:
                text_line = get_text_from_list_bboxes(line_sorted_boxes)
                page_lines_content.append(text_line)

            page_content = "\n".join(page_lines_content)
            pages_content_per_page.append(page_content)

        self.text = "\n".join(pages_content_per_page)
