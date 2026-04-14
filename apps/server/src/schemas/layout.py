from typing import Optional, Any
from pydantic import BaseModel, Field


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
    order: Optional[int] = None
    content: Optional[Any] = None
