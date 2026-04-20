"""Templating routes.

POST   /v1/templatings/                       -> upload ODT, create templating
GET    /v1/templatings/{id}                   -> get templating by id
GET    /v1/templatings/                       -> list templatings (by group or user)
PATCH  /v1/templatings/{id}                  -> update name/description/entity_zone
DELETE /v1/templatings/{id}                  -> delete templating (+ S3 object)
"""

from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ocr_backend.connectors import s3_client_connector
from ocr_backend.core.security.factory import TokenVerifier
from ocr_backend.core.security.token import RequestContext
from src.connector.db_connector import AsyncSessionLocal
from src.schemas.templating import TemplatingModel, TemplatingUpdateModel
from src.services.templating_service import TemplatingService

router = APIRouter(tags=["Templatings"], prefix="/templatings")

CtxDep = Annotated[RequestContext, Depends(TokenVerifier)]
ServiceDep = Annotated[TemplatingService, Depends(TemplatingService)]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


DbDep = Annotated[AsyncSession, Depends(get_db)]

ACCEPTED_MIME = "application/vnd.oasis.opendocument.text"


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Upload an ODT template")
async def create_templating(
    ctx: CtxDep,
    service: ServiceDep,
    db: DbDep,
    file: Annotated[UploadFile, File(...)],
    name: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    group_id: Annotated[str, Form()] = "DEFAULT",
) -> TemplatingModel:
    if ctx.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if file.content_type != ACCEPTED_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Only ODT files are accepted (got {file.content_type})",
        )
    return await service.create_templating(
        db=db,
        file=file,
        name=name,
        description=description,
        user_id=ctx.user_id,
        group_id=group_id,
        s3_connector=s3_client_connector,
    )


@router.get("/{templating_id}", summary="Get a templating by id")
async def get_templating(
    templating_id: str,
    ctx: CtxDep,
    service: ServiceDep,
    db: DbDep,
) -> TemplatingModel:
    if ctx.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return await service.get_templating_by_id(db, templating_id)


@router.get("/", summary="List templatings (paginated)")
async def list_templatings(
    ctx: CtxDep,
    service: ServiceDep,
    db: DbDep,
    group_id: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    if ctx.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if group_id:
        items = await service.get_templatings_by_group_id(db, group_id, page, page_size)
        total = await service.count_templatings_by_group_id(db, group_id)
    else:
        items = await service.get_templatings_by_user_id(db, ctx.user_id, page, page_size)
        total = await service.count_templatings_by_user_id(db, ctx.user_id)

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.patch("/{templating_id}", summary="Update a templating")
async def update_templating(
    templating_id: str,
    form_data: TemplatingUpdateModel,
    ctx: CtxDep,
    service: ServiceDep,
    db: DbDep,
) -> TemplatingModel:
    if ctx.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return await service.update_templating(db, templating_id, form_data)


@router.delete("/{templating_id}", summary="Delete a templating")
async def delete_templating(
    templating_id: str,
    ctx: CtxDep,
    service: ServiceDep,
    db: DbDep,
) -> TemplatingModel:
    if ctx.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return await service.delete_templating_by_id(
        db=db,
        templating_id=templating_id,
        s3_connector=s3_client_connector,
        user_id=ctx.user_id,
    )
