from fastapi import APIRouter, HTTPException, Depends

from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier
from src.schemas.templates import template_table, TemplateModel


template_router = APIRouter(tags=["Template"])
WORKER_NAME = "worker.tasks.ocr"


@template_router.get("/template/{template_id}", response_model=TemplateModel, deprecated=True)
async def get_template(template_id: str):
    template = template_table.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@template_router.get("/v1/template/{template_id}", response_model=TemplateModel)
async def v1_get_template(template_id: str, depends: RequestContext = Depends(TokenVerifier)):
    template = await get_template(template_id)
    if depends.user_id != template.user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this template")
    return template


@template_router.get("/templates/user/{user_id}", response_model=list[TemplateModel])
async def get_templates_by_user(user_id: str):
    templates = template_table.get_templates_by_user_id(user_id)
    return templates


@template_router.get("/templates/group/{group_id}", response_model=list[TemplateModel])
async def get_templates_by_group(group_id: str):
    templates = template_table.get_templates_by_group_id(group_id)
    return templates


@template_router.delete("/template/{template_id}", response_model=TemplateModel)
async def delete_template(
    template_id: str,
    depends: RequestContext = Depends(TokenVerifier),
):
    if not depends.is_admin:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this template",
        )
    deleted_template = template_table.delete_template_by_id(template_id)
    if not deleted_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return deleted_template


@template_router.delete("/templates/user/{user_id}", response_model=list[TemplateModel])
async def delete_templates_by_user(user_id: str, depends: RequestContext = Depends(TokenVerifier)):
    if not depends.is_admin:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete these templates",
        )
    deleted_templates = template_table.delete_templates_by_user_id(user_id)
    if not deleted_templates:
        raise HTTPException(status_code=404, detail="No templates found for user")
    return deleted_templates


@template_router.delete("/templates/group/{group_id}", response_model=list[TemplateModel])
async def delete_templates_by_group(group_id: str, depends: RequestContext = Depends(TokenVerifier)):
    if depends.is_admin is False:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete templates for this group",
        )
    deleted_templates = template_table.delete_templates_by_group_id(group_id)
    if not deleted_templates:
        raise HTTPException(status_code=404, detail="No templates found for group")
    return deleted_templates
