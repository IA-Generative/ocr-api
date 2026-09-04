"""Tests de `KeycloakToken`.

Ce chemin décide de chaque 401 de l'API : soit via une clé d'API (`Authorization:
Bearer <API key>`, pour les appels machine-à-machine), soit via le cookie de session
posé par `/api/auth/callback` (BFF) - le navigateur ne transporte plus de jeton Keycloak.
"""

import pytest
from fastapi import HTTPException, Request, status

from ocr_backend.core.security import keycloak_client
from ocr_backend.core.security.factory import ApiToken, KeycloakToken
from ocr_backend.core.security.session import SessionStore

SESSION_COOKIE_NAME = "ocr_session"


def make_request(headers: dict | None = None, cookies: dict | None = None) -> Request:
    header_list = [(k.encode(), v.encode()) for k, v in (headers or {}).items()]
    if cookies:
        cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
        header_list.append((b"cookie", cookie_header.encode()))
    scope = {
        "type": "http",
        "headers": header_list,
    }
    return Request(scope)


@pytest.fixture(autouse=True)
def _session_cookie_name(monkeypatch):
    monkeypatch.setattr(keycloak_client.keycloak_settings, "SESSION_COOKIE_NAME", SESSION_COOKIE_NAME)


@pytest.fixture
def store(fake_redis) -> SessionStore:
    store = SessionStore(redis_client=fake_redis, keycloak_openid=None, ttl_seconds=3600)
    return store


@pytest.fixture
def keycloak_verifier(monkeypatch, store) -> KeycloakToken:
    monkeypatch.setenv("API_KEYS", "secret-api-key")
    monkeypatch.setattr(keycloak_client, "session_store", store)
    return KeycloakToken()


IDENTITY = {
    "user_id": "user-123",
    "email": "user@example.com",
    "first_name": "Alice",
    "last_name": "Martin",
    "roles": ["admin"],
    "groups": ["ocr-users"],
    "is_admin": True,
}


def make_session(store: SessionStore) -> str:
    token_response = {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "expires_in": 3600,
        "refresh_expires_in": 7200,
    }
    return store.create(token_response, IDENTITY)


def test_valid_session_cookie_fills_context(keycloak_verifier, store):
    sid = make_session(store)

    ctx = keycloak_verifier(make_request(cookies={SESSION_COOKIE_NAME: sid}))

    assert ctx.user_id == "user-123"
    assert ctx.email == "user@example.com"
    assert ctx.groups == ["ocr-users"]
    assert ctx.roles == ["admin"]
    assert ctx.is_admin is True
    assert ctx.token == "access-token"


def test_claims_override_client_supplied_identity_headers(keycloak_verifier, store):
    """Les en-têtes X-* sont fournis par l'appelant : la session doit primer."""
    sid = make_session(store)

    ctx = keycloak_verifier(
        make_request(
            headers={"x-user-id": "attacker", "x-roles": "admin"},
            cookies={SESSION_COOKIE_NAME: sid},
        )
    )

    assert ctx.user_id == "user-123"


def test_missing_cookie_is_rejected(keycloak_verifier):
    with pytest.raises(HTTPException) as exc:
        keycloak_verifier(make_request())
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_unknown_session_is_rejected(keycloak_verifier):
    with pytest.raises(HTTPException) as exc:
        keycloak_verifier(make_request(cookies={SESSION_COOKIE_NAME: "does-not-exist"}))
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_expired_refresh_token_is_rejected(keycloak_verifier, store):
    token_response = {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "expires_in": 0,
        "refresh_expires_in": 0,
    }
    sid = store.create(token_response, IDENTITY)

    with pytest.raises(HTTPException) as exc:
        keycloak_verifier(make_request(cookies={SESSION_COOKIE_NAME: sid}))
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_key_does_not_inherit_roles_from_headers(monkeypatch):
    """Un porteur de clé d'API ne doit pas devenir admin via l'en-tête X-Roles."""
    monkeypatch.setenv("API_KEYS", "secret-api-key")
    verifier = ApiToken()

    ctx = verifier(
        make_request(
            headers={
                "authorization": "Bearer secret-api-key",
                "x-roles": "admin",
            }
        )
    )

    assert ctx.user_id == "api_user"
    assert ctx.roles == []
    assert ctx.is_admin is False


def test_api_key_path_short_circuits_session_lookup(keycloak_verifier, store, monkeypatch):
    def boom(_sid):
        raise AssertionError("a valid API key must not need a session lookup")

    monkeypatch.setattr(store, "get", boom)

    ctx = keycloak_verifier(make_request(headers={"authorization": "Bearer secret-api-key", "x-roles": "admin"}))

    assert ctx.user_id == "api_user"
    assert ctx.is_admin is False


def test_unknown_api_key_falls_through_to_session(keycloak_verifier, store):
    sid = make_session(store)

    ctx = keycloak_verifier(
        make_request(
            headers={"authorization": "Bearer not-an-api-key"},
            cookies={SESSION_COOKIE_NAME: sid},
        )
    )

    assert ctx.user_id == "user-123"
