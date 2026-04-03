from fastapi import APIRouter, Depends, HTTPException, Query

from ocr_backend.core.security.factory import TokenVerifier
from ocr_backend.core.security.token import RequestContext
from src.schemas.annotations import (
    AnnotationModel,
    AnnotationStats,
    AnnotationUpsertForm,
    task_table,
)
from src.schemas.pagination import Pagination

router = APIRouter(tags=["Annotations"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_annotation_or_404(content_hash: str, user_id: str) -> AnnotationModel:
    annotation = task_table.get_by_content_hash(content_hash, user_id)
    if annotation is None:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get(
    "/annotations/{content_hash}",
    response_model=AnnotationModel,
    summary="Get annotation by file hash",
)
async def get_annotation(
    content_hash: str,
    ctx: RequestContext = Depends(TokenVerifier),
):
    if ctx.is_admin:
        # Admin gets the full annotation regardless of ownership
        annotation = task_table.get_by_content_hash(content_hash)
        if annotation is None:
            raise HTTPException(status_code=404, detail="Annotation not found")
        return annotation

    annotation = _get_annotation_or_404(content_hash, ctx.user_id)
    return annotation


@router.get(
    "/annotations/user/",
    response_model=Pagination[AnnotationModel],
    summary="Get paginated annotations for the current user",
)
async def get_annotations_by_user(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    ctx: RequestContext = Depends(TokenVerifier),
):
    if ctx.user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    count = task_table.count_by_user_id(ctx.user_id)
    items = task_table.get_by_user_id(ctx.user_id, page=page, page_size=page_size)
    return Pagination[AnnotationModel](total=count, page=page, page_size=page_size, items=items or [])


@router.put(
    "/annotations/{content_hash}",
    response_model=AnnotationModel,
    summary="Create or update annotation for a file (upsert)",
)
async def upsert_annotation(
    content_hash: str,
    form_data: AnnotationUpsertForm,
    ctx: RequestContext = Depends(TokenVerifier),
):
    if ctx.user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Force user_id from token — never trust client-supplied value
    form_data = form_data.model_copy(update={"user_id": ctx.user_id})
    return task_table.upsert(content_hash, form_data)


@router.delete(
    "/annotations/{content_hash}",
    response_model=AnnotationModel,
    summary="Delete annotation by file hash",
)
async def delete_annotation(
    content_hash: str,
    ctx: RequestContext = Depends(TokenVerifier),
):
    _get_annotation_or_404(content_hash)
    if not ctx.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    deleted = task_table.delete_by_content_hash(content_hash)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return deleted


@router.get(
    "/stats/annotations",
    response_model=AnnotationStats,
    summary="Annotation metrics (global + current user)",
)
async def get_annotation_stats(
    ctx: RequestContext = Depends(TokenVerifier),
):
    if ctx.user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return task_table.statistics(ctx.user_id)
