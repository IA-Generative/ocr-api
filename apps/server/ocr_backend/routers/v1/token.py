"""Token management routes.

POST /v1/tokens    -> create token (authenticated)
GET  /v1/tokens    -> list tokens for current user
DELETE /v1/tokens/{id} -> delete token by id (owner)
"""

from typing import List
from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from ocr_backend.core.security.factory import TokenVerifier
from ocr_backend.core.security.token import RequestContext

from src.models.token import TokenCreate, TokenResponse
from src.services.token_service import (
    create_token,
    get_token_by_id,
    get_tokens_by_user,
    delete_token_by_id,
)

logger = getLogger(__name__)


router = APIRouter(tags=["Tokens"], prefix="/tokens")


@router.post("/", summary="Create a token for the current user")
async def create_user_token(
    payload: TokenCreate, ctx: Annotated[RequestContext, Depends(TokenVerifier)]
) -> TokenResponse:
    user_id = ctx.user_id
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    try:
        row = create_token(
            user_id=user_id,
            token_str=payload.token,
            expires=payload.expired_at,
            roles=payload.roles,
        )
        # Return token metadata (response model may hide token value)
        logger.info(f"Token created for user_id={user_id}")
        return TokenResponse.model_validate(row)
    except Exception as e:
        logger.error(f"Error creating token for user_id={user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", summary="List tokens for current user")
async def list_user_tokens(
    ctx: Annotated[RequestContext, Depends(TokenVerifier)],
) -> List[TokenResponse]:
    user_id = ctx.user_id
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    rows = get_tokens_by_user(user_id)
    logger.info(f"Retrieved {len(rows)} tokens for user_id={user_id}")
    return [TokenResponse.model_validate(r) for r in rows]


@router.delete("/{token_id}", summary="Delete token by id for current user")
async def delete_user_token(token_id: str, ctx: Annotated[RequestContext, Depends(TokenVerifier)]):
    user_id = ctx.user_id
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    token = get_token_by_id(token_id)
    if not token or token.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    ok = delete_token_by_id(token_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete token",
        )
    logger.info(f"Deleted token_id={token_id} for user_id={user_id}")
    return {"deleted": True}
