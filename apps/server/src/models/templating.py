from datetime import datetime

from sqlalchemy import JSON, BigInteger, Column, Integer, String
from src.connector.db_connector import Base


class Templating(Base):
    __tablename__ = "templating"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    group_id = Column(String, nullable=False, default="DEFAULT")

    source_file = Column(String, nullable=False)
    source_task_id = Column(String, nullable=True)
    extracting_status = Column(String, nullable=True)
    total_page = Column(Integer, nullable=False, default=0)
    created_at = Column(BigInteger, default=lambda: int(datetime.now().timestamp()))
    updated_at = Column(
        BigInteger,
        default=lambda: int(datetime.now().timestamp()),
        onupdate=lambda: int(datetime.now().timestamp()),
    )
    entity_zone = Column(JSON, nullable=True)
    entity_names = Column(JSON, nullable=True)

    extras = Column(JSON, nullable=True)
