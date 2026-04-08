"""GET /v1/models — list available OCR models."""

from fastapi import APIRouter, Depends


from ocr_backend.core.security.factory import ApiToken
from ocr_backend.core.security.token import RequestContext

from .schemas import ModelList, _AVAILABLE_MODELS

router = APIRouter(
    tags=["Models"],
    prefix="/models",
)


@router.get(
    path="/",
    summary="List available OCR models",
)
def list_models(
    _ctx: RequestContext = Depends(ApiToken()),
) -> ModelList:
    """
    Example response
    ----------------
    {
        "object": "list",
        "data": [
            {"id": "ocr-v1", "object": "model", "created": 1712345678, "owned_by": "ocr-api"},
            {"id": "ocr-v1-fast", "object": "model", "created": 1712345678, "owned_by": "ocr-api"}
        ]
    }
    """
    return ModelList(data=_AVAILABLE_MODELS)
