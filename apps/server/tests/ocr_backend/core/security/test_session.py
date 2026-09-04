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
        "id_token": "id-token",
        "expires_in": expires_in,
        "refresh_expires_in": refresh_expires_in,
    }


@pytest.fixture
def keycloak_openid():
    openid = Mock()
    openid.client_id = "ocr"
    openid.userinfo.return_value = {
        "sub": "user-123",
        "email": "user@example.com",
        "given_name": "Alice",
        "family_name": "Martin",
        "groups": ["ocr-users"],
        "resource_access": {"ocr": {"roles": ["admin"]}},
    }
    return openid


@pytest.fixture
def store(fake_redis, keycloak_openid) -> SessionStore:
    return SessionStore(redis_client=fake_redis, keycloak_openid=keycloak_openid, ttl_seconds=3600)  # gitleaks:allow


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


def test_ensure_fresh_rederives_roles_from_refreshed_token(store, keycloak_openid):
    keycloak_openid.refresh_token.return_value = token_response(expires_in=3600, refresh_expires_in=7200)
    keycloak_openid.userinfo.return_value = {
        "sub": "user-123",
        "email": "user@example.com",
        "resource_access": {"ocr": {"roles": []}},
    }
    sid = store.create(token_response(expires_in=5), IDENTITY)
    session = store.get(sid)

    refreshed = store.ensure_fresh(sid, session)

    assert refreshed.roles == []
    assert refreshed.is_admin is False


def test_ensure_fresh_keeps_previous_roles_when_userinfo_refresh_fails(store, keycloak_openid):
    keycloak_openid.refresh_token.return_value = token_response(expires_in=3600, refresh_expires_in=7200)
    keycloak_openid.userinfo.side_effect = ConnectionError("keycloak unreachable")
    sid = store.create(token_response(expires_in=5), IDENTITY)
    session = store.get(sid)

    refreshed = store.ensure_fresh(sid, session)

    assert refreshed is not None
    assert refreshed.roles == ["admin"]
    assert refreshed.is_admin is True


def test_ensure_fresh_second_caller_reuses_first_callers_refresh(store, keycloak_openid, fake_redis):
    keycloak_openid.refresh_token.return_value = token_response(expires_in=3600, refresh_expires_in=7200)
    sid = store.create(token_response(expires_in=5), IDENTITY)
    session = store.get(sid)

    # Simulate a concurrent request already holding the refresh lock.
    fake_redis.set(f"bff_session_refresh_lock:{sid}", "1", nx=True, ex=10)
    fake_redis.setex(
        f"bff_session:{sid}",
        3600,
        session.model_copy(update={"expires_at": time.time() + 3600}).model_dump_json(),
    )

    refreshed = store.ensure_fresh(sid, session)

    assert refreshed is not None
    assert refreshed.expires_at > time.time() + 3000
    keycloak_openid.refresh_token.assert_not_called()


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


def test_check_rate_limit_allows_up_to_the_limit(store):
    for _ in range(3):
        assert store.check_rate_limit("ip-1", limit=3, window_seconds=60) is True

    assert store.check_rate_limit("ip-1", limit=3, window_seconds=60) is False


def test_check_rate_limit_tracks_keys_independently(store):
    for _ in range(3):
        store.check_rate_limit("ip-1", limit=3, window_seconds=60)

    assert store.check_rate_limit("ip-2", limit=3, window_seconds=60) is True
