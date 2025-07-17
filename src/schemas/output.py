from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from src.schemas.box import Bbox, Checkbox
from src.schemas.layout import Layout
from src.utils.bboxes import sort_bboxes_reading_order, get_text_from_list_bboxes
from src.schemas.template import FormEntry


class Page(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    page: int
    page_url: Optional[str] = None
    boxes: List[Bbox] = Field(default_factory=list, description="Detections")
    layouts: List[Layout] = Field(default_factory=list, description="Layout definition")
    checkboxes: List[Checkbox] = Field(default_factory=list, description="Checkbox definition")
    form_entries: List[FormEntry] = Field(default_factory=list, description="Form extraction")


class OCRResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str
    model_name: str
    created_at: int
    updated_at: int
    version: str
    total_pages: int
    pages: List[Page]
    extras: Optional[dict] = None
    text: Optional[str] = ""

    def set_text(self, delta_y: float = 0.005):
        self.text = ""
        pages_content_per_page = []

        for i, page in enumerate(self.pages):
            page_lines_content = [f"{20 * '-'} Page: {i + 1} {20 * '-'}"]
            checkboxes: List[Bbox] = []
            if len(page.checkboxes):
                for c_box in page.checkboxes:
                    bbox = Bbox(
                        x=c_box.x,
                        y=c_box.y,
                        width=c_box.width,
                        height=c_box.height,
                        confidence=c_box.confidence,
                        text="[x]" if c_box.is_checked else "[ ]",
                    )
                    checkboxes.append(bbox)

            sorted_bboxes = sort_bboxes_reading_order(bboxes=page.boxes + checkboxes, delta_y=delta_y)
            for line_sorted_boxes in sorted_bboxes:
                text_line = get_text_from_list_bboxes(line_sorted_boxes)
                page_lines_content.append(text_line)

            page_content = "\n".join(page_lines_content)
            pages_content_per_page.append(page_content)

        self.text = "\n".join(pages_content_per_page)
