import time
from unittest.mock import Mock

import pytest

from ocr_backend.core.security.session import SessionStore

IDENTITY = {
    "user_id": "user-123",
    "email": "user@example.com",
    "first_name": "Alice",
    "last_name": "Martin",
    "roles": ["admin"],
    "groups": ["ocr-users"],
    "is_admin": True,
}


def token_response(expires_in=300, refresh_expires_in=3600):
    return {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "expires_in": expires_in,
        "refresh_expires_in": refresh_expires_in,
    }


@pytest.fixture
def keycloak_openid():
    return Mock()


@pytest.fixture
def store(fake_redis, keycloak_openid) -> SessionStore:
    return SessionStore(redis_client=fake_redis, keycloak_openid=keycloak_openid, ttl_seconds=3600)


def test_create_then_get_round_trips_identity(store):
    sid = store.create(token_response(), IDENTITY)

    session = store.get(sid)

    assert session is not None
    assert session.user_id == "user-123"
    assert session.roles == ["admin"]
    assert session.is_admin is True
    assert session.access_token == "access-token"


def test_get_unknown_session_returns_none(store):
    assert store.get("does-not-exist") is None


def test_ensure_fresh_returns_session_unchanged_when_not_near_expiry(store, keycloak_openid):
    sid = store.create(token_response(expires_in=3600), IDENTITY)
    session = store.get(sid)

    refreshed = store.ensure_fresh(sid, session)

    assert refreshed == session
    keycloak_openid.refresh_token.assert_not_called()


def test_ensure_fresh_refreshes_when_access_token_near_expiry(store, keycloak_openid):
    keycloak_openid.refresh_token.return_value = token_response(expires_in=3600, refresh_expires_in=7200)
    sid = store.create(token_response(expires_in=5), IDENTITY)
    session = store.get(sid)

    refreshed = store.ensure_fresh(sid, session)

    assert refreshed is not None
    assert refreshed.expires_at > time.time() + 3000
    keycloak_openid.refresh_token.assert_called_once_with("refresh-token")
    # The refreshed session must be the one persisted, not just returned in memory.
    assert store.get(sid).access_token == refreshed.access_token


def test_ensure_fresh_deletes_session_when_refresh_token_expired(store, keycloak_openid):
    sid = store.create(token_response(expires_in=5, refresh_expires_in=1), IDENTITY)
    time.sleep(1.1)
    session = store.get(sid)

    refreshed = store.ensure_fresh(sid, session)

    assert refreshed is None
    assert store.get(sid) is None
    keycloak_openid.refresh_token.assert_not_called()


def test_ensure_fresh_deletes_session_when_keycloak_refresh_fails(store, keycloak_openid):
    keycloak_openid.refresh_token.side_effect = ConnectionError("keycloak unreachable")
    sid = store.create(token_response(expires_in=5), IDENTITY)
    session = store.get(sid)

    refreshed = store.ensure_fresh(sid, session)

    assert refreshed is None
    assert store.get(sid) is None


def test_delete_removes_session(store):
    sid = store.create(token_response(), IDENTITY)

    store.delete(sid)

    assert store.get(sid) is None


def test_pending_auth_round_trips_and_is_single_use(store):
    store.save_pending("state-abc", "verifier-xyz", "/tasks/42")

    pending = store.pop_pending("state-abc")

    assert pending is not None
    assert pending.code_verifier == "verifier-xyz"
    assert pending.next_path == "/tasks/42"
    assert store.pop_pending("state-abc") is None


def test_pop_pending_unknown_state_returns_none(store):
    assert store.pop_pending("never-saved") is None
