"""Schema and model for Tokens only.

This module defines the SQLAlchemy `Token` model and lightweight Pydantic
schemas used by the server API for creating and returning tokens.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String

from src.connector.db_connector import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    created_at = Column(BigInteger, default=lambda: int(datetime.now().timestamp()))
    expired_at = Column(BigInteger, nullable=True)
    token = Column(String, nullable=False, unique=True, index=True)
    roles = Column(String, nullable=True)


class TokenModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    token: str | None = None
    roles: Optional[str] = None
    created_at: int
    expired_at: Optional[int] = None


class TokenCreate(BaseModel):
    model_config = ConfigDict()
    token: str
    expired_at: Optional[int] = None
    roles: Optional[str] = None
    extras: Optional[Dict[str, Any]] = None


class TokenResponse(TokenModel):
    token: Optional[str] = None
