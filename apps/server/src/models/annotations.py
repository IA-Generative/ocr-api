import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import JSON, BigInteger, Column, String, func

from src.connector.db_connector import Base, get_db
from src.logger import logger


class TasksAnnotations(Base):
    __tablename__ = "annotations"

    # Primary key is the file hash: annotations survive task/file deletion
    content_hash = Column(String, primary_key=True, nullable=False)

    user_id = Column(String, nullable=False)
    output = Column(JSON, nullable=True)

    created_at = Column(BigInteger, default=lambda: int(datetime.now().timestamp()))
    updated_at = Column(
        BigInteger,
        default=lambda: int(datetime.now().timestamp()),
        onupdate=lambda: int(datetime.now().timestamp()),
    )

    extras = Column(JSON, nullable=True)


class BoxAnnotation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    index: int | None = Field(None, description="Index of the bbox in the original detection list")
    x: float
    y: float
    width: float
    height: float
    text: Optional[str] = None
    validation: Optional[str] = Field(default=None, description="Validation state: 'valid', 'invalid', or null")
    private: bool = Field(default=False, description="Whether the annotation is private or not")


class ClassificationAnnotation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    label: str
    description: Optional[str] = None


class PageAnnotation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    page: int
    boxes: list[BoxAnnotation] = Field(default_factory=list, description="Detections")
    classifications: list[ClassificationAnnotation] = Field(default_factory=list, description="Classifications")
    private: bool = Field(default=False, description="Whether the annotation is private or not")


class TaskAnnotationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    output: list[PageAnnotation] = Field(default_factory=list, description="Page Annotations")
    extras: Optional[dict] = None

    def sanitize(self) -> "TaskAnnotationBase":
        """Return a copy with private content masked.

        - Private pages are dropped entirely.
        - On visible pages, private bboxes are replaced with a blank white bbox
          (same position/size, no text).
        """
        sanitized_pages: list[PageAnnotation] = []
        for page in self.output:
            if page.private:
                continue
            cleaned_boxes = [
                (
                    BoxAnnotation(
                        index=box.index,
                        x=box.x,
                        y=box.y,
                        width=box.width,
                        height=box.height,
                    )
                    if box.private
                    else box
                )
                for box in page.boxes
            ]
            sanitized_pages.append(
                PageAnnotation(
                    page=page.page,
                    boxes=cleaned_boxes,
                    classifications=page.classifications,
                )
            )
        return TaskAnnotationBase(output=sanitized_pages, extras=self.extras)


class AnnotationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    output: list[PageAnnotation] = Field(default_factory=list, description="Page Annotations")
    extras: Optional[dict] = None


class AnnotationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    content_hash: str
    user_id: str
    output: list[PageAnnotation] = Field(default_factory=list)
    extras: Optional[Dict[str, Any]] = None
    created_at: int
    updated_at: int


class AnnotationUpsertForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    output: list[PageAnnotation] = Field(default_factory=list)
    extras: Optional[dict] = None


# ---------------------------------------------------------------------------
# Metrics models
# ---------------------------------------------------------------------------


class AnnotationStatsGlobal(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total_annotations: int
    total_unique_files: int  # distinct content_hash


class AnnotationStatsUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    total_annotations: int
    total_unique_files: int


class AnnotationStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    global_stats: AnnotationStatsGlobal
    user_stats: AnnotationStatsUser


# ---------------------------------------------------------------------------
# Table / service
# ---------------------------------------------------------------------------


class TaskAnnotationTable:
    def __init__(self, get_db):
        self.get_db = get_db

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def upsert(self, content_hash: str, form_data: AnnotationUpsertForm) -> Optional[AnnotationModel]:
        """Insert or replace the annotation for a given file hash."""
        with self.get_db() as db:
            row = db.query(TasksAnnotations).filter(TasksAnnotations.content_hash == content_hash).first()
            now = int(time.time())
            output_dump = [p.model_dump() for p in form_data.output]

            if row is None:
                row = TasksAnnotations(
                    content_hash=content_hash,
                    user_id=form_data.user_id,
                    output=output_dump,
                    extras=form_data.extras,
                    created_at=now,
                    updated_at=now,
                )
                db.add(row)
            else:
                row.user_id = form_data.user_id
                row.output = output_dump
                row.extras = form_data.extras
                row.updated_at = now

            db.commit()
            db.refresh(row)
            return AnnotationModel.model_validate(row)

    def delete_by_content_hash(self, content_hash: str) -> Optional[AnnotationModel]:
        with self.get_db() as db:
            row = db.query(TasksAnnotations).filter(TasksAnnotations.content_hash == content_hash).first()
            if not row:
                logger.warning(f"Annotation with content_hash {content_hash} not found.")
                return None
            model = AnnotationModel.model_validate(row)
            db.delete(row)
            db.commit()
            return model

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_content_hash(self, content_hash: str, user_id: str | None = None) -> Optional[AnnotationModel]:
        with self.get_db() as db:
            row = (
                db.query(TasksAnnotations)
                .filter(
                    TasksAnnotations.content_hash == content_hash,
                    TasksAnnotations.user_id == user_id if user_id else True,
                )
                .first()
            )

            if not row:
                return None
            return AnnotationModel.model_validate(row)

    def get_by_user_id(self, user_id: str, page: int = 1, page_size: int = 20) -> List[AnnotationModel]:
        offset = (page - 1) * page_size
        with self.get_db() as db:
            rows = (
                db.query(TasksAnnotations)
                .filter(TasksAnnotations.user_id == user_id)
                .offset(offset)
                .limit(page_size)
                .all()
            )
            return [AnnotationModel.model_validate(r) for r in rows]

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def statistics(self, user_id: str) -> AnnotationStats:
        with self.get_db() as db:
            total = db.query(func.count(TasksAnnotations.content_hash)).scalar() or 0
            total_unique = db.query(func.count(func.distinct(TasksAnnotations.content_hash))).scalar() or 0

            user_total = (
                db.query(func.count(TasksAnnotations.content_hash)).filter(TasksAnnotations.user_id == user_id).scalar()
                or 0
            )
            user_unique = (
                db.query(func.count(func.distinct(TasksAnnotations.content_hash)))
                .filter(TasksAnnotations.user_id == user_id)
                .scalar()
                or 0
            )

            return AnnotationStats(
                global_stats=AnnotationStatsGlobal(
                    total_annotations=total,
                    total_unique_files=total_unique,
                ),
                user_stats=AnnotationStatsUser(
                    user_id=user_id,
                    total_annotations=user_total,
                    total_unique_files=user_unique,
                ),
            )

    def count_by_user_id(self, user_id: str) -> int:
        with self.get_db() as db:
            return (
                db.query(func.count(TasksAnnotations.content_hash)).filter(TasksAnnotations.user_id == user_id).scalar()
                or 0
            )


task_table = TaskAnnotationTable(get_db)
