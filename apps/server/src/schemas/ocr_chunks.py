from typing import List

from pydantic import BaseModel, ConfigDict, Field


class OcrChunkBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content_hash: str
    page_nums: List[int] = Field(
        ...,
        description="0-based page indices covered by this chunk. Usually a single page, "
        "but can contain several when a paragraph crosses a page boundary.",
    )
    bbox_indices: List[int] = Field(default_factory=list)
    text: str
    model_name: str
    vector: List[float]
    vector_size: int


class OcrChunkModel(OcrChunkBase):
    id: str
    created_at: int


class OcrChunkUpsertForm(BaseModel):
    """Payload sent by the client to index a batch of chunks for a file."""

    chunks: List[OcrChunkBase] = Field(default_factory=list)


class OcrChunkSearchRequest(BaseModel):
    """Payload for semantic search over a file\'s chunks."""

    query_vector: List[float] = Field(..., description="Dense query embedding")
    top_k: int = Field(default=5, ge=1, le=50)


class OcrChunkSearchResult(BaseModel):
    """A single search hit returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    content_hash: str
    page_nums: List[int]
    bbox_indices: List[int]
    text: str
    model_name: str
    score: float
