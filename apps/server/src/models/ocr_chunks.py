"""
OCR Chunk table — stores vectorised text chunks extracted from OCR pages.

Each chunk represents a contiguous group of bboxes on a page. The vector field
contains the dense embedding produced by the configured feature extractor model.
Chunks are the unit fed to the chatbot's semantic search.
"""

from __future__ import annotations

import time
import uuid
from typing import List


from sqlalchemy import JSON, BigInteger, Column, Integer, String
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator
from src.schemas.ocr_chunks import OcrChunkBase, OcrChunkModel, OcrChunkSearchResult


class _JsonbOrJson(TypeDecorator):
    """Uses PostgreSQL JSONB when available, falls back to JSON (e.g. SQLite)."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import JSONB

            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())


JSONB = _JsonbOrJson  # type: ignore[assignment,misc]

from src.connector.db_connector import Base, get_db  # noqa: E402


# ---------------------------------------------------------------------------
# SQLAlchemy model
# ---------------------------------------------------------------------------


class OcrChunksTable(Base):
    __tablename__ = "ocr_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # File identifier — matches annotations.content_hash
    content_hash = Column(String, nullable=False, index=True)

    # Pages covered by this chunk (JSON list[int], 0-based).
    # A chunk can span multiple pages when a paragraph crosses a page boundary.
    page_nums = Column(JSONB, nullable=False, default=list)

    # Serialised list of bbox indices involved in this chunk (e.g. [0, 1, 2])
    bbox_indices = Column(JSONB, nullable=False, default=list)

    # Raw text of the chunk
    text = Column(String, nullable=False)

    # Embedding
    model_name = Column(String, nullable=False)
    vector = Column(JSONB, nullable=False)  # list[float] serialised as JSONB
    vector_size = Column(Integer, nullable=False)

    created_at = Column(BigInteger, default=lambda: int(time.time()))


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------


class OcrChunkRepository:
    def __init__(self, get_db):
        self.get_db = get_db

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def upsert_bulk(self, chunks: List[OcrChunkBase]) -> List[OcrChunkModel]:
        """Insert or replace chunks.

        A chunk is identified by (content_hash, page_nums, bbox_indices JSON).
        If the same key already exists it is overwritten (delete + insert).
        """
        results: List[OcrChunkModel] = []
        with self.get_db() as db:
            for chunk in chunks:
                key_indices = chunk.bbox_indices
                # Remove existing chunk with same position
                existing = (
                    db.query(OcrChunksTable)
                    .filter(
                        OcrChunksTable.content_hash == chunk.content_hash,
                        OcrChunksTable.page_nums == chunk.page_nums,
                        OcrChunksTable.bbox_indices == key_indices,
                    )
                    .first()
                )
                if existing:
                    row_id = existing.id
                    db.delete(existing)
                else:
                    row_id = str(uuid.uuid4())

                now = int(time.time())
                row = OcrChunksTable(
                    id=row_id,
                    content_hash=chunk.content_hash,
                    page_nums=chunk.page_nums,
                    bbox_indices=chunk.bbox_indices,
                    text=chunk.text,
                    model_name=chunk.model_name,
                    vector=chunk.vector,
                    vector_size=chunk.vector_size,
                    created_at=now,
                )
                db.add(row)
                db.flush()
                results.append(OcrChunkModel.model_validate(row))
            db.commit()
        return results

    def delete_by_content_hash(self, content_hash: str) -> int:
        """Delete all chunks for a file. Returns the count deleted."""
        with self.get_db() as db:
            rows = db.query(OcrChunksTable).filter(OcrChunksTable.content_hash == content_hash).all()
            count = len(rows)
            for r in rows:
                db.delete(r)
            db.commit()
        return count

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_content_hash(self, content_hash: str) -> List[OcrChunkModel]:
        with self.get_db() as db:
            rows = db.query(OcrChunksTable).filter(OcrChunksTable.content_hash == content_hash).all()
            return [OcrChunkModel.model_validate(r) for r in rows]

    # ------------------------------------------------------------------
    # Search (cosine similarity in Python — no pgvector required)
    # ------------------------------------------------------------------

    def search(
        self,
        content_hash: str,
        query_vector: List[float],
        top_k: int | None = 5,
        threshold: float | None = None,
    ) -> List[OcrChunkSearchResult]:
        """Return the top-k most similar chunks for a given file.

        Uses cosine similarity computed in Python. This is sufficient for
        typical document sizes (a few hundred chunks per file). For large-scale
        deployments, migrate to pgvector or Qdrant.
        """
        chunks = self.get_by_content_hash(content_hash)
        if not chunks:
            return []

        scored: List[tuple[float, OcrChunkModel]] = []
        q_norm = _l2_norm(query_vector)

        for chunk in chunks:
            if len(chunk.vector) != len(query_vector):
                continue
            score = _cosine_similarity(query_vector, chunk.vector, q_norm)
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)

        if threshold is not None:
            scored = [(score, chunk) for score, chunk in scored if score >= threshold]
        if top_k is not None:
            scored = scored[:top_k]

        return [
            OcrChunkSearchResult(
                id=c.id,
                content_hash=c.content_hash,
                page_nums=c.page_nums,
                bbox_indices=c.bbox_indices,
                text=c.text,
                model_name=c.model_name,
                score=round(score, 6),
            )
            for score, c in scored
        ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _l2_norm(v: List[float]) -> float:
    return sum(x * x for x in v) ** 0.5 or 1.0


def _cosine_similarity(a: List[float], b: List[float], a_norm: float) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    b_norm = _l2_norm(b)
    return dot / (a_norm * b_norm)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

ocr_chunk_repo = OcrChunkRepository(get_db)
