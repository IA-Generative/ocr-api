from pydantic import BaseModel, Field
from typing import List, Union, Optional


class TableCell(BaseModel):
    value: Union[str, "TableBlock"] = Field(
        ...,
        description="Cell content. Can be a string or a nested table if hierarchical structure exists.",
    )
    rowspan: int = Field(1, description="Number of rows this cell spans.")
    colspan: int = Field(1, description="Number of columns this cell spans.")


class TableRow(BaseModel):
    cells: List[TableCell] = Field(..., description="List of cells in the row, ordered left to right.")


class TableHeader(BaseModel):
    name: str = Field(..., description="Header label.")
    children: Optional[List["TableHeader"]] = Field(None, description="Nested headers for hierarchical tables.")


class TableContent(BaseModel):
    headers: Optional[List[TableHeader]] = Field(None, description="Table headers, possibly hierarchical.")
    rows: List[TableRow] = Field(..., description="Table rows in reading order.")


class TableBlock(BaseModel):
    type: str = Field("table", description="Block type identifier.")
    content: TableContent = Field(..., description="Structured table content.")
