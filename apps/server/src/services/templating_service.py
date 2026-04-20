import os
import uuid

import aiofiles
import aiofiles.tempfile
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.connector.broker_connector import celery_app
from src.logger import logger
from src.repositories.templating_repository import TemplatingRepository
from src.schemas.templating import (
    TemplatingCreateModel,
    TemplatingModel,
    TemplatingUpdateModel,
)
from src.schemas.task import TaskForm, TaskOperation, TaskStatus, CeleryTaskName
from src.schemas.input import InputForm
from src.repositories.task_repository import TaskRepository
import hashlib


class TemplatingService:
    def __init__(self):
        self.templating_repo = TemplatingRepository()
        self.task_repo = TaskRepository()

    async def create_templating(
        self,
        db: AsyncSession,
        file: UploadFile,
        name: str,
        description: str,
        user_id: str,
        group_id: str,
        s3_connector,
    ) -> TemplatingModel:
        """
        Upload ODT file to S3, create templating record.
        Returns the created templating.
        """
        templating_id = str(uuid.uuid4())

        hasher = hashlib.md5()
        async with aiofiles.tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename or "")[1]
        ) as tmp:
            tmp_path = tmp.name
            chunk_size = 8192
            while chunk := await file.read(chunk_size):
                hasher.update(chunk)
                await tmp.write(chunk)
        content_hash = hasher.hexdigest()

        try:
            source_file = s3_connector.save(user_id, templating_id, tmp_path)
            logger.debug(f"Templating {templating_id} saved to S3: {source_file}")

        finally:
            os.remove(tmp_path)

        templating = await self.templating_repo.insert_new_templating(
            db=db,
            form_data=TemplatingCreateModel(
                id=templating_id,
                name=name,
                description=description,
                user_id=user_id,
                group_id=group_id,
                source_file=source_file,
                source_task_id=None,
                total_page=1,
                entity_zone=None,
                extras=None,
            ),
        )
        task_form = TaskForm(
            id=templating.id,
            type=TaskOperation.TEMPLATING_EXTRACTION.value,
            group_id=group_id,
            status=TaskStatus.QUEUED.value,
            percentage=0.0,
            parameters=None,
            input=InputForm(
                storage_file_path=source_file,
                raw_filename=file.filename,
                content_type=file.content_type,
                ext=os.path.splitext(file.filename or "")[1],
                size=file.size or 0,
                group_id=group_id,
            ),
            output=None,
            parent_id=None,
            extras=None,
            content_hash=content_hash,
            user_id=user_id,
        )
        task = await self.task_repo.insert_new_task(db, user_id=user_id, form_data=task_form)
        celery_app.send_task(
            CeleryTaskName.TEMPLATING_EXTRACTION_TASK.value,
            args=[task.model_dump()],
            task_id=task.id,
        )
        return templating

    async def get_templating_by_id(self, db: AsyncSession, templating_id: str) -> TemplatingModel:
        return await self.templating_repo.get_templating_by_id(db, templating_id)

    async def get_templatings_by_group_id(
        self,
        db: AsyncSession,
        group_id: str,
        page: int = 1,
        page_size: int = 10,
    ) -> list[TemplatingModel]:
        return await self.templating_repo.get_templatings_by_group_id(db, group_id, page, page_size)

    async def count_templatings_by_group_id(self, db: AsyncSession, group_id: str) -> int:
        return await self.templating_repo.count_templatings_by_group_id(db, group_id)

    async def get_templatings_by_user_id(
        self,
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
    ) -> list[TemplatingModel]:
        return await self.templating_repo.get_templatings_by_user_id(db, user_id, page, page_size)

    async def count_templatings_by_user_id(self, db: AsyncSession, user_id: str) -> int:
        return await self.templating_repo.count_templatings_by_user_id(db, user_id)

    async def update_templating(
        self,
        db: AsyncSession,
        templating_id: str,
        form_data: TemplatingUpdateModel,
    ) -> TemplatingModel:
        return await self.templating_repo.update_templating(db, templating_id, form_data)

    async def update_extracting_status(
        self,
        db: AsyncSession,
        templating_id: str,
        status: str,
        total_page: int | None = None,
    ) -> TemplatingModel:
        return await self.templating_repo.update_extracting_status(db, templating_id, status, total_page)

    async def delete_templating_by_id(
        self,
        db: AsyncSession,
        templating_id: str,
        s3_connector,
        user_id: str,
    ) -> TemplatingModel:
        await self.templating_repo.get_templating_by_id(db, templating_id)

        try:
            s3_connector.delete_by_task_id(user_id, templating_id)
        except Exception as e:
            logger.warning(f"Could not delete S3 object for templating {templating_id}: {e}")

        return await self.templating_repo.delete_templating_by_id(db, templating_id)

    async def delete_templatings_by_group_id(
        self,
        db: AsyncSession,
        group_id: str,
        s3_connector,
    ) -> list[TemplatingModel]:
        templatings = await self.templating_repo.get_templatings_by_group_id(db, group_id, page=1, page_size=10_000)

        for t in templatings:
            try:
                s3_connector.delete_by_task_id(t.user_id, t.id)
            except Exception as e:
                logger.warning(f"Could not delete S3 object for templating {t.id}: {e}")

        return await self.templating_repo.delete_templatings_by_group_id(db, group_id)
