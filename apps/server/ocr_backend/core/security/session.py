import secrets
import time
from typing import Optional

from keycloak import KeycloakOpenID
from pydantic import BaseModel
from redis import Redis

from src.logger import logger

_SESSION_KEY_PREFIX = "bff_session:"
_PENDING_KEY_PREFIX = "bff_oauth_pending:"
_PENDING_TTL_SECONDS = 5 * 60
# Refresh proactively before actual expiry, so a request never races a token that
# expires mid-flight.
_REFRESH_SKEW_SECONDS = 30


class SessionData(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: float
    refresh_expires_at: float
    user_id: str
    email: str
    first_name: str
    last_name: str
    roles: list[str]
    groups: list[str]
    is_admin: bool


class PendingAuth(BaseModel):
    code_verifier: str
    next_path: str


class SessionStore:
    def __init__(self, redis_client: Redis, keycloak_openid: KeycloakOpenID, ttl_seconds: int):
        self._redis = redis_client
        self._keycloak_openid = keycloak_openid
        self._ttl_seconds = ttl_seconds

    def create(self, token_response: dict, identity: dict) -> str:
        now = time.time()
        session = SessionData(
            access_token=token_response["access_token"],
            refresh_token=token_response["refresh_token"],
            expires_at=now + token_response["expires_in"],
            refresh_expires_at=now + token_response["refresh_expires_in"],
            **identity,
        )
        sid = secrets.token_urlsafe(32)
        self._redis.setex(_SESSION_KEY_PREFIX + sid, self._ttl_seconds, session.model_dump_json())
        return sid

    def get(self, sid: str) -> Optional[SessionData]:
        raw = self._redis.get(_SESSION_KEY_PREFIX + sid)
        if not raw:
            return None
        return SessionData.model_validate_json(raw)

    def ensure_fresh(self, sid: str, session: SessionData) -> Optional[SessionData]:
        if session.expires_at > time.time() + _REFRESH_SKEW_SECONDS:
            return session

        if session.refresh_expires_at <= time.time():
            self.delete(sid)
            return None

        try:
            token_response = self._keycloak_openid.refresh_token(session.refresh_token)
        except Exception as e:
            logger.warning("Failed to refresh Keycloak session: %s", e)
            self.delete(sid)
            return None

        now = time.time()
        refreshed = session.model_copy(
            update={
                "access_token": token_response["access_token"],
                "refresh_token": token_response["refresh_token"],
                "expires_at": now + token_response["expires_in"],
                "refresh_expires_at": now + token_response["refresh_expires_in"],
            }
        )
        self._redis.setex(_SESSION_KEY_PREFIX + sid, self._ttl_seconds, refreshed.model_dump_json())
        return refreshed

    def delete(self, sid: str) -> None:
        self._redis.delete(_SESSION_KEY_PREFIX + sid)

    def save_pending(self, state: str, code_verifier: str, next_path: str) -> None:
        pending = PendingAuth(code_verifier=code_verifier, next_path=next_path)
        self._redis.setex(_PENDING_KEY_PREFIX + state, _PENDING_TTL_SECONDS, pending.model_dump_json())

    def pop_pending(self, state: str) -> Optional[PendingAuth]:
        key = _PENDING_KEY_PREFIX + state
        raw = self._redis.get(key)
        if not raw:
            return None
        self._redis.delete(key)
        return PendingAuth.model_validate_json(raw)
