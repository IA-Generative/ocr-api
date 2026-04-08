from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ocr_backend.core.security.factory import TokenVerifier
from ocr_backend.core.security.token import RequestContext
from src.schemas.ocr_chunks import (
    OcrChunkModel,
    OcrChunkSearchRequest,
    OcrChunkSearchResult,
    OcrChunkUpsertForm,
    ocr_chunk_repo,
)

router = APIRouter(tags=["OCR Chunks"])


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post(
    "/ocr-chunks/{content_hash}",
    response_model=List[OcrChunkModel],
    summary="Index (upsert) a batch of vectorised OCR chunks for a file",
)
async def upsert_chunks(
    content_hash: str,
    form: OcrChunkUpsertForm,
    ctx: RequestContext = Depends(TokenVerifier),
):
    """Store or replace vectorised chunks for a given file.

    Each chunk must carry:
    - ``page_num``: 0-based page index
    - ``bbox_indices``: list of bbox indices from that page that compose the chunk
    - ``text``: raw text of the chunk
    - ``model_name``: name of the embedding model
    - ``vector``: dense embedding (list of floats)
    - ``vector_size``: dimension of the embedding

    The ``content_hash`` in the URL is used as the scope key; any
    ``content_hash`` value in each chunk payload is overridden by the URL
    parameter to prevent mismatches.
    """
    # Force content_hash from URL
    for chunk in form.chunks:
        chunk.content_hash = content_hash

    return ocr_chunk_repo.upsert_bulk(form.chunks)


@router.get(
    "/ocr-chunks/{content_hash}",
    response_model=List[OcrChunkModel],
    summary="List all chunks indexed for a file",
)
async def list_chunks(
    content_hash: str,
    ctx: RequestContext = Depends(TokenVerifier),
):
    return ocr_chunk_repo.get_by_content_hash(content_hash)


@router.post(
    "/ocr-chunks/{content_hash}/search",
    response_model=List[OcrChunkSearchResult],
    summary="Semantic search over a file's indexed chunks",
)
async def search_chunks(
    content_hash: str,
    body: OcrChunkSearchRequest,
    ctx: RequestContext = Depends(TokenVerifier),
):
    """Return the top-k chunks whose vector is closest to ``query_vector``.

    The results include ``page_num`` and ``bbox_indices`` so the frontend can
    highlight the exact bounding boxes involved in each answer.
    """
    results = ocr_chunk_repo.search(
        content_hash=content_hash,
        query_vector=body.query_vector,
        top_k=body.top_k,
    )
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No indexed chunks found for content_hash '{content_hash}'.",
        )
    return results


@router.delete(
    "/ocr-chunks/{content_hash}",
    summary="Delete all chunks for a file",
)
async def delete_chunks(
    content_hash: str,
    ctx: RequestContext = Depends(TokenVerifier),
):
    count = ocr_chunk_repo.delete_by_content_hash(content_hash)
    return {"deleted": count}
