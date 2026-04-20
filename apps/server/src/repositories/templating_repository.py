import time
import uuid

from fastapi import HTTPException, status as http_status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger
from src.models.templating import Templating
from src.schemas.templating import (
    TemplatingCreateModel,
    TemplatingModel,
    TemplatingUpdateModel,
)


class TemplatingRepository:
    async def insert_new_templating(self, db: AsyncSession, form_data: TemplatingCreateModel) -> TemplatingModel:
        _id = str(uuid.uuid4()) if not form_data.id else form_data.id

        result = Templating(
            id=_id,
            name=form_data.name,
            description=form_data.description,
            user_id=getattr(form_data, "user_id", None),
            extras=form_data.extras,
            group_id=form_data.group_id,
            source_file=form_data.source_file,
            source_task_id=form_data.source_task_id,
            total_page=form_data.total_page,
            entity_zone=([ez.model_dump() for ez in form_data.entity_zone] if form_data.entity_zone else None),
            extracting_status=None,
            created_at=int(time.time()),
            updated_at=int(time.time()),
            entity_names=(form_data.entity_names.model_dump() if form_data.entity_names else None),
        )
        db.add(result)
        await db.commit()
        await db.refresh(result)
        return TemplatingModel.model_validate(result)

    async def get_templating_by_id(self, db: AsyncSession, templating_id: str) -> TemplatingModel:
        templating = await db.get(Templating, templating_id)
        if not templating:
            logger.warning(f"Templating with id {templating_id} not found.")
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Templating with id {templating_id} not found.",
            )
        return TemplatingModel.model_validate(templating)

    async def get_templatings_by_group_id(
        self, db: AsyncSession, group_id: str, page: int = 1, page_size: int = 10
    ) -> list[TemplatingModel]:
        offset = (page - 1) * page_size
        result = await db.execute(
            select(Templating)
            .filter(Templating.group_id == group_id)
            .order_by(Templating.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        templatings = result.scalars().all()
        return [TemplatingModel.model_validate(t) for t in templatings]

    async def count_templatings_by_group_id(self, db: AsyncSession, group_id: str) -> int:
        result = await db.execute(select(func.count(Templating.id)).filter(Templating.group_id == group_id))
        return result.scalar_one()

    async def get_templatings_by_user_id(
        self, db: AsyncSession, user_id: str, page: int = 1, page_size: int = 10
    ) -> list[TemplatingModel]:
        offset = (page - 1) * page_size
        result = await db.execute(
            select(Templating)
            .filter(Templating.user_id == user_id)
            .order_by(Templating.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        templatings = result.scalars().all()
        return [TemplatingModel.model_validate(t) for t in templatings]

    async def count_templatings_by_user_id(self, db: AsyncSession, user_id: str) -> int:
        result = await db.execute(select(func.count(Templating.id)).filter(Templating.user_id == user_id))
        return result.scalar_one()

    async def update_templating(
        self, db: AsyncSession, templating_id: str, form_data: TemplatingUpdateModel
    ) -> TemplatingModel:
        templating = await db.get(Templating, templating_id)
        if not templating:
            logger.warning(f"Templating with id {templating_id} not found.")
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Templating with id {templating_id} not found.",
            )

        updates = form_data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            if key == "entity_zone" and value is not None:
                templating.entity_zone = [ez.model_dump() if hasattr(ez, "model_dump") else ez for ez in value]
            elif key == "entity_names" and value is not None:
                templating.entity_names = value.model_dump() if hasattr(value, "model_dump") else value
            elif hasattr(templating, key):
                setattr(templating, key, value)

        templating.updated_at = int(time.time())
        await db.commit()
        await db.refresh(templating)
        return TemplatingModel.model_validate(templating)

    async def update_extracting_status(
        self,
        db: AsyncSession,
        templating_id: str,
        status: str,
        total_page: int | None = None,
    ) -> TemplatingModel:
        templating = await db.get(Templating, templating_id)
        if not templating:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Templating with id {templating_id} not found.",
            )
        templating.extracting_status = status
        if total_page is not None:
            templating.total_page = total_page
        templating.updated_at = int(time.time())
        await db.commit()
        await db.refresh(templating)
        return TemplatingModel.model_validate(templating)

    async def delete_templating_by_id(self, db: AsyncSession, templating_id: str) -> TemplatingModel:
        templating = await db.get(Templating, templating_id)
        if not templating:
            logger.warning(f"Templating with id {templating_id} not found.")
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Templating with id {templating_id} not found.",
            )
        await db.delete(templating)
        await db.commit()
        return TemplatingModel.model_validate(templating)

    async def delete_templatings_by_group_id(self, db: AsyncSession, group_id: str) -> list[TemplatingModel]:
        result = await db.execute(select(Templating).filter(Templating.group_id == group_id))
        templatings = result.scalars().all()
        for t in templatings:
            await db.delete(t)
        await db.commit()
        return [TemplatingModel.model_validate(t) for t in templatings]
