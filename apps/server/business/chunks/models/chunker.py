"""OcrChunker — splits OCR pages into overlapping text chunks and vectorises them.

Strategy
--------
Two chunking strategies are available:

* ``SLIDING_WINDOW`` (default): groups consecutive bboxes within a page using a
  fixed window of N bboxes and an overlap of K bboxes.  This is the most
  predictable strategy and works well for dense, uniform text.

* ``PARAGRAPH``: splits on spatial gaps between bboxes (a gap larger than
  ``gap_threshold`` times the average bbox height signals a paragraph break).
  It then falls back to the sliding-window strategy inside paragraphs that are
  longer than ``max_chunk_bboxes``.

A chunk that spans a page boundary (only possible in PARAGRAPH mode when a
paragraph continues on the next page — detected by proximity to the bottom of
the page) sets ``page_nums`` to the list of page indices it covers.

Vectorisation
-------------
The chunk's vector is produced by ``embed_text()``.  The default implementation
uses a simple character-frequency bag-of-words normalised to unit length so that
the system works without any deep-learning dependency.  Replace ``embed_text``
with a call to your real embedding model (sentence-transformers, OpenAI, etc.)
when needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from src.logger import logger
from src.schemas.box import Bbox
from src.schemas.ocr_chunks import OcrChunkBase
from src.schemas.output import Page
import openai
from src.config.openai import OpenAISettings

openai_settings = OpenAISettings()
# ---------------------------------------------------------------------------
# Strategy enum
# ---------------------------------------------------------------------------


class ChunkingStrategy(str, Enum):
    SLIDING_WINDOW = "sliding_window"
    PARAGRAPH = "paragraph"


# ---------------------------------------------------------------------------
# Internal data class
# ---------------------------------------------------------------------------


@dataclass
class _RawChunk:
    page_nums: List[int]
    bbox_indices: List[int]
    text: str


# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------


class OcrChunker:
    """Converts a list of OCR pages into persistable ``OcrChunkBase`` objects.

    Parameters
    ----------
    model_name:
        Name of the embedding model used to produce vectors.
        Stored verbatim in each ``OcrChunkBase``.
    vector_size:
        Dimension of the output embedding.
    strategy:
        ``SLIDING_WINDOW`` or ``PARAGRAPH``.
    window_size:
        Number of bboxes per chunk (sliding-window strategy).
    overlap:
        Number of bboxes shared between consecutive chunks.
    max_chunk_bboxes:
        Maximum number of bboxes in a single chunk (paragraph strategy).
    gap_threshold:
        Multiplier of the average bbox height used to detect paragraph breaks.
    """

    def __init__(
        self,
        model_name: str = openai_settings.EMBEDDINGS_MODEL,
        vector_size: int = 128,
        strategy: ChunkingStrategy = ChunkingStrategy.PARAGRAPH,
        window_size: int = 5,
        overlap: int = 1,
        max_chunk_bboxes: int = 10,
        gap_threshold: float = 1.5,
    ) -> None:
        self.model_name = model_name
        self.vector_size = vector_size
        self.strategy = strategy
        self.window_size = window_size
        self.overlap = overlap
        self.max_chunk_bboxes = max_chunk_bboxes
        self.gap_threshold = gap_threshold
        self.client_openai = openai.OpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            base_url=openai_settings.OPENAI_BASE_URL,
            timeout=openai_settings.OPENAI_TIMEOUT,
            max_retries=openai_settings.OPENAI_MAX_RETRIES,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chunk_pages(self, content_hash: str, pages: List[Page]) -> List[OcrChunkBase]:
        """Return all chunks for a document, ready for DB insertion."""
        raw_chunks = self._extract_raw_chunks(pages)
        result: List[OcrChunkBase] = []
        for i in range(0, len(raw_chunks), 10):  # Embed in batches of 10 for efficiency
            batch = raw_chunks[i : i + 10]
            texts = [rc.text for rc in batch]
            vectors = self.embed_text(texts)
            for rc, vector in zip(batch, vectors):
                result.append(
                    OcrChunkBase(
                        content_hash=content_hash,
                        page_nums=rc.page_nums,
                        bbox_indices=rc.bbox_indices,
                        text=rc.text,
                        model_name=self.model_name,
                        vector=vector,
                        vector_size=len(vector),
                    )
                )

        logger.debug(
            f"[OcrChunker] {content_hash}: {len(result)} chunks from {len(pages)} pages "
            f"(strategy={self.strategy.value})"
        )
        return result

    # ------------------------------------------------------------------
    # Embedding (override for a real model)
    # ------------------------------------------------------------------

    def embed_text(self, texts: list[str]) -> List[List[float]]:
        """Produce a dense embedding for ``text``.

        Default: normalised character-frequency vector of size ``vector_size``.
        Replace this method with a real embedding call (sentence-transformers,
        OpenAI embeddings, etc.) in production.
        """
        logger.debug(f"Embedding {len(texts)} texts with model {self.model_name}")
        res = self.client_openai.embeddings.create(input=texts, model=self.model_name)
        logger.debug(
            f"Embedding {len(texts)} texts with model {self.model_name}: data_len={len(getattr(res, 'data', []))}"
        )
        # The SDK returns objects in `res.data` with an `embedding` attribute
        return [item.embedding for item in res.data]

    # ------------------------------------------------------------------
    # Strategy dispatch
    # ------------------------------------------------------------------

    def _extract_raw_chunks(self, pages: List[Page]) -> List[_RawChunk]:
        if self.strategy == ChunkingStrategy.PARAGRAPH:
            return self._paragraph_chunks(pages)
        return self._sliding_window_chunks(pages)

    # ------------------------------------------------------------------
    # Sliding-window strategy
    # ------------------------------------------------------------------

    def _sliding_window_chunks(self, pages: List[Page]) -> List[_RawChunk]:
        chunks: List[_RawChunk] = []
        step = max(1, self.window_size - self.overlap)

        for page in pages:
            boxes: List[Bbox] = page.boxes or []
            if not boxes:
                continue
            # Sort bboxes in reading order (top-to-bottom, left-to-right)
            sorted_indices = sorted(
                range(len(boxes)),
                key=lambda i: (round(boxes[i].y, 2), boxes[i].x),
            )
            n = len(sorted_indices)
            start = 0
            while start < n:
                end = min(start + self.window_size, n)
                indices = sorted_indices[start:end]
                text = " ".join(boxes[i].text.strip() for i in indices if boxes[i].text).strip()
                if text:
                    chunks.append(
                        _RawChunk(
                            page_nums=[page.page],
                            bbox_indices=indices,
                            text=text,
                        )
                    )
                start += step
        return chunks

    # ------------------------------------------------------------------
    # Paragraph strategy
    # ------------------------------------------------------------------

    def _paragraph_chunks(self, pages: List[Page]) -> List[_RawChunk]:
        """Group bboxes into paragraphs, then slide within large paragraphs."""
        chunks: List[_RawChunk] = []

        for page in pages:
            boxes: List[Bbox] = page.boxes or []
            if not boxes:
                continue

            sorted_indices = sorted(
                range(len(boxes)),
                key=lambda i: (round(boxes[i].y, 2), boxes[i].x),
            )

            # Compute average bbox height for gap detection
            heights = [boxes[i].height for i in sorted_indices if boxes[i].height > 0]
            avg_h = (sum(heights) / len(heights)) if heights else 0.02
            threshold = avg_h * self.gap_threshold

            # Group into paragraphs
            paragraphs: List[List[int]] = []
            current: List[int] = [sorted_indices[0]]
            for prev_idx, curr_idx in zip(sorted_indices, sorted_indices[1:]):
                gap = boxes[curr_idx].y - (boxes[prev_idx].y + boxes[prev_idx].height)
                if gap > threshold:
                    paragraphs.append(current)
                    current = [curr_idx]
                else:
                    current.append(curr_idx)
            paragraphs.append(current)

            # Convert paragraphs to chunks (split long ones)
            for para in paragraphs:
                if len(para) <= self.max_chunk_bboxes:
                    text = " ".join(boxes[i].text.strip() for i in para if boxes[i].text).strip()
                    if text:
                        chunks.append(_RawChunk(page_nums=[page.page], bbox_indices=para, text=text))
                else:
                    # Slide within the paragraph
                    step = max(1, self.max_chunk_bboxes - self.overlap)
                    for start in range(0, len(para), step):
                        sub = para[start : start + self.max_chunk_bboxes]
                        text = " ".join(boxes[i].text.strip() for i in sub if boxes[i].text).strip()
                        if text:
                            chunks.append(_RawChunk(page_nums=[page.page], bbox_indices=sub, text=text))

        return chunks
