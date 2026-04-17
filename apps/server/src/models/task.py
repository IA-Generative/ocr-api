from datetime import datetime

from sqlalchemy import FLOAT, JSON, BigInteger, Column, Integer, String

from src.connector.db_connector import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    status = Column(String, default="queued")
    user_id = Column(String, nullable=False)
    group_id = Column(String, nullable=True)
    percentage = Column(FLOAT, nullable=False)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    position = Column(Integer, nullable=True)
    created_at = Column(BigInteger, default=lambda: int(datetime.now().timestamp()))
    updated_at = Column(
        BigInteger,
        default=lambda: int(datetime.now().timestamp()),
        onupdate=lambda: int(datetime.now().timestamp()),
    )
    parameters = Column(JSON, nullable=True)

    extras = Column(JSON, nullable=True)
    content_hash = Column(String, nullable=True, index=True, unique=False)
    parent_id = Column(String, nullable=True)
