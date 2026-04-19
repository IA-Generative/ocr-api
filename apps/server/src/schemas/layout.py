from typing import Optional, Any
from pydantic import BaseModel, Field
from src.schemas.layouts.image import ImageBlock
from src.schemas.layouts.formula import FormulaBlock
from src.schemas.layouts.table import TableBlock


# labels
# document title, paragraph title, text, page number, abstract, table, references,
# footnotes, header, footer, algorithm, formula, formula number, image,
# table, seal, figure_table title, chart, and sidebar text and lists of references


class Layout(BaseModel):
    cls_id: int = Field(..., description="Class ID, an integer.")
    label: str = Field(..., description="Class label, a string.")
    score: float = Field(..., description="Confidence score of the bounding box, a float.")
    coordinate: list[float] = Field(
        ...,
        description="Coordinates of the bounding box, a list of floats in the format [xmin, ymin, xmax, ymax]",
    )
    order: Optional[int] = Field(None, description="Order of the layout element.")
    content: Optional[Any] = Field(None, description="Optional content of the layout element.")
    block: Optional[ImageBlock | FormulaBlock | TableBlock] = Field(
        None, description="Optional block content, can be an image, formula, or table."
    )
