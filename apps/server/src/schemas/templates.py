import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, BigInteger, Column, Integer, String
from src.connector.db_connector import Base, get_db
from src.logger import logger
from src.schemas.input import RegionOfInterest


class Template(Base):
    __tablename__ = "templates"

    id = Column(String, primary_key=True)
    description = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    group_id = Column(String, nullable=False, default="DEFAULT")
    source_file = Column(String, nullable=False)
    source_task_id = Column(String, nullable=True)
    page_number = Column(Integer, nullable=False, default=0)
    vector = Column(JSON, nullable=True)
    model_name = Column(String, nullable=True)
    vector_size = Column(Integer, nullable=True)
    interest_zone = Column(JSON, nullable=True)
    created_at = Column(BigInteger, default=lambda: int(datetime.now().timestamp()))
    updated_at = Column(
        BigInteger,
        default=lambda: int(datetime.now().timestamp()),
        onupdate=lambda: int(datetime.now().timestamp()),
    )

    extras = Column(JSON, nullable=True)


class TemplateModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    description: Optional[str] = None
    source_file: str
    source_task_id: Optional[str] = None
    page_number: int = 0
    vector: Optional[list[float]] = None
    model_name: Optional[str] = None
    vector_size: Optional[int] = None
    created_at: int
    updated_at: int
    extras: Optional[Dict[str, Any]] = None
    interest_zone: Optional[RegionOfInterest] = None


class TemplateForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    description: Optional[str] = None
    source_file: str
    source_task_id: Optional[str] = None
    page_number: int = 0
    vector: Optional[list[float]] = None
    model_name: Optional[str] = None
    vector_size: Optional[int] = None
    extras: Optional[Dict[str, Any]] = None
    interest_zone: Optional[RegionOfInterest] = None


class TemplateUpdateForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    description: Optional[str] = None
    source_file: Optional[str] = None
    source_task_id: Optional[str] = None
    page_number: Optional[int] = None
    vector: Optional[list[float]] = None
    model_name: Optional[str] = None
    vector_size: Optional[int] = None
    extras: Optional[Dict[str, Any]] = None
    interest_zone: Optional[RegionOfInterest] = None


class TemplateTable:
    def __init__(self, get_db):
        self.get_db = get_db

    def insert_new_template(self, form_data: TemplateForm) -> Optional[TemplateModel]:
        with self.get_db() as db:
            knowledge = TemplateModel(
                **{
                    **form_data.model_dump(),
                    "id": str(uuid.uuid4()),
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )

            result = Template(**knowledge.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            return TemplateModel.model_validate(result)

    def get_template_by_id(self, template_id: str) -> Optional[TemplateModel]:
        with self.get_db() as db:
            template = db.query(Template).filter(Template.id == template_id).first()
            if not template:
                logger.warning(f"Template with id {template_id} not found.")
                return None
            return TemplateModel.model_validate(template)

    def update_template(self, template_id: str, form_data: TemplateUpdateForm) -> Optional[TemplateModel]:
        with self.get_db() as db:
            template = db.query(Template).filter(Template.id == template_id).first()
            if not template:
                logger.warning(f"Template with id {template_id} not found.")
                return None

            updates = form_data.model_dump(exclude_unset=True)

            for key, value in updates.items():
                if hasattr(template, key):
                    setattr(template, key, value)

            template.updated_at = int(time.time())
            db.commit()
            db.refresh(template)
            return TemplateModel.model_validate(template)

    def delete_template_by_id(self, template_id: str) -> Optional[TemplateModel]:
        with self.get_db() as db:
            template = db.query(Template).filter(Template.id == template_id).first()
            if not template:
                logger.warning(f"Template with id {template_id} not found.")
                return None
            db.delete(template)
            db.commit()
            return TemplateModel.model_validate(template)

    def get_templates_by_user_id(
        self, user_id: str, page: int = 1, page_size: int = 10
    ) -> Optional[List[TemplateModel]]:
        offset = (page - 1) * page_size
        with self.get_db() as db:
            templates = db.query(Template).filter(Template.user_id == user_id).offset(offset).limit(page_size).all()

            if not templates:
                logger.warning(f"No templates found for user {user_id}.")
                return None

            return [TemplateModel.model_validate(template) for template in templates]

    def delete_templates_by_user_id(self, user_id: str) -> Optional[List[TemplateModel]]:
        with self.get_db() as db:
            templates_to_delete = db.query(Template).filter(Template.user_id == user_id).all()

            if not templates_to_delete:
                logger.warning(f"No templates found for user {user_id}.")
                return None

            for template in templates_to_delete:
                db.delete(template)
            db.commit()

            return [TemplateModel.model_validate(template) for template in templates_to_delete]

    def get_templates_by_group_id(
        self, group_id: str, page: int = 1, page_size: int = 10
    ) -> Optional[List[TemplateModel]]:
        offset = (page - 1) * page_size
        with self.get_db() as db:
            templates = db.query(Template).filter(Template.group_id == group_id).offset(offset).limit(page_size).all()

            if not templates:
                logger.warning(f"No templates found for group {group_id}.")
                return None

            return [TemplateModel.model_validate(template) for template in templates]

    def delete_templates_by_group_id(self, group_id: str) -> Optional[List[TemplateModel]]:
        with self.get_db() as db:
            templates_to_delete = db.query(Template).filter(Template.group_id == group_id).all()

            if not templates_to_delete:
                logger.warning(f"No templates found for group {group_id}.")
                return None

            for template in templates_to_delete:
                db.delete(template)
            db.commit()

            return [TemplateModel.model_validate(template) for template in templates_to_delete]


template_table = TemplateTable(get_db)
