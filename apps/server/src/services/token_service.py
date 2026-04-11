"""Service helpers to interact with the `tokens` table.

Provides simple CRUD helpers used by API routers or background jobs.
"""

from datetime import datetime
import uuid
from typing import List, Optional

from src.connector.db_connector import get_db
from src.schemas.token import Token as TokenTable, TokenModel


def create_token(
    user_id: str,
    token_str: str,
    expires: Optional[int] = None,
    roles: Optional[str] = None,
) -> TokenModel:
    """Create and persist a new token row.

    Returns the created token as a Pydantic `TokenModel`.
    """
    with get_db() as db:
        row = TokenTable(
            id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=int(datetime.now().timestamp()),
            expired_at=expires,
            token=token_str,
            roles=roles,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        token = TokenModel.model_validate(row)
        token.token = None  # Don't return the token value by default for security
        return token


def get_token_by_id(token_id: str) -> Optional[TokenModel]:
    with get_db() as db:
        row = db.query(TokenTable).filter(TokenTable.id == token_id).first()
        if not row:
            return None
        token = TokenModel.model_validate(row)
        token.token = None  # Don't return the token value by default for security
        return token


def verify_token(user_id: str, token_str: str) -> Optional[TokenModel]:
    """Check if a token string is valid (exists and not expired).

    Returns the corresponding `TokenModel` if valid, or `None` if invalid.
    """
    token = get_token_by_user_and_token(user_id, token_str)
    if not token:
        return None
    if token.expired_at and token.expired_at < int(datetime.now().timestamp()):
        # Token is expired, consider it invalid
        return None
    token.token = None  # Don't return the token value for security
    return token


def get_token_by_value(token_str: str) -> Optional[TokenModel]:
    with get_db() as db:
        row = db.query(TokenTable).filter(TokenTable.token == token_str).first()
        if not row:
            return None
        token = TokenModel.model_validate(row)
        token.token = None  # Don't return the token value by default for security
        return token


def get_token_by_user_and_token(user_id: str, token_str: str) -> Optional[TokenModel]:
    with get_db() as db:
        row = db.query(TokenTable).filter(TokenTable.user_id == user_id, TokenTable.token == token_str).first()
        if not row:
            return None
        token = TokenModel.model_validate(row)
        token.token = None  # Don't return the token value by default for security
        return token


def get_tokens_by_user(user_id: str) -> List[TokenModel]:
    with get_db() as db:
        rows = db.query(TokenTable).filter(TokenTable.user_id == user_id).all()
        tokens = [TokenModel.model_validate(r) for r in rows]
        for token in tokens:
            token.token = None  # Don't return the token value by default for security
        return tokens


def delete_token_by_id(token_id: str) -> bool:
    with get_db() as db:
        row = db.query(TokenTable).filter(TokenTable.id == token_id).first()
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True


def revoke_token_by_value(token_str: str) -> bool:
    with get_db() as db:
        row = db.query(TokenTable).filter(TokenTable.token == token_str).first()
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True
