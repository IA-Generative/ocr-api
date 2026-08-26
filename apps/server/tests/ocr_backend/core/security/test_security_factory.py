"""Tests de `KeycloakToken`, jusque-là non couvert.

Ce chemin décide de chaque 401 de l'API : il mérite des tests, d'autant que ses échecs
sont silencieux côté Keycloak (200 `{"active": false}`, sans motif).
"""

import pytest
from fastapi import HTTPException, Request, status

from ocr_backend.core.security.factory import ApiToken, KeycloakToken


def make_request(headers: dict) -> Request:
    scope = {
        "type": "http",
        "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
    }
    return Request(scope)


@pytest.fixture
def keycloak_verifier(monkeypatch) -> KeycloakToken:
    monkeypatch.setenv("KEYCLOAK_CLIENT_ID", "ocr-api")
    monkeypatch.setenv("API_KEYS", "secret-api-key")
    return KeycloakToken()


ACTIVE_CLAIMS = {
    "active": True,
    "sub": "user-123",
    "email": "user@example.com",
    "groups": ["ocr-users"],
    "resource_access": {"ocr-api": {"roles": ["admin"]}},
}


def test_active_token_fills_context_from_claims(keycloak_verifier, monkeypatch):
    monkeypatch.setattr(keycloak_verifier.keycloak_openid, "introspect", lambda _token: ACTIVE_CLAIMS)

    ctx = keycloak_verifier(make_request({"authorization": "Bearer good-token"}))

    assert ctx.user_id == "user-123"
    assert ctx.email == "user@example.com"
    assert ctx.groups == ["ocr-users"]
    assert ctx.roles == ["admin"]
    assert ctx.is_admin is True


def test_claims_override_client_supplied_identity_headers(keycloak_verifier, monkeypatch):
    """Les en-têtes X-* sont fournis par l'appelant : le jeton doit primer."""
    monkeypatch.setattr(
        keycloak_verifier.keycloak_openid,
        "introspect",
        lambda _token: {**ACTIVE_CLAIMS, "resource_access": {"ocr-api": {"roles": []}}},
    )

    ctx = keycloak_verifier(
        make_request(
            {
                "authorization": "Bearer good-token",
                "x-user-id": "attacker",
                "x-roles": "admin",
            }
        )
    )

    assert ctx.user_id == "user-123"
    assert ctx.roles == []
    assert ctx.is_admin is False


def test_inactive_token_is_rejected(keycloak_verifier, monkeypatch, caplog):
    """Keycloak >= 26.6.2 répond `active: false` quand le client d'introspection
    n'est pas dans l'`aud` du jeton. Le rejet doit être tracé, pas silencieux."""
    monkeypatch.setattr(keycloak_verifier.keycloak_openid, "introspect", lambda _token: {"active": False})

    with caplog.at_level("WARNING"):
        with pytest.raises(HTTPException) as exc:
            keycloak_verifier(make_request({"authorization": "Bearer stale-token"}))

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "audience" in caplog.text


def test_introspection_failure_is_rejected(keycloak_verifier, monkeypatch):
    def boom(_token):
        raise ConnectionError("keycloak unreachable")

    monkeypatch.setattr(keycloak_verifier.keycloak_openid, "introspect", boom)

    with pytest.raises(HTTPException) as exc:
        keycloak_verifier(make_request({"authorization": "Bearer any-token"}))
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_missing_token_is_rejected_without_calling_keycloak(keycloak_verifier, monkeypatch):
    def boom(_token):
        raise AssertionError("introspection must not be attempted without a token")

    monkeypatch.setattr(keycloak_verifier.keycloak_openid, "introspect", boom)

    with pytest.raises(HTTPException) as exc:
        keycloak_verifier(make_request({}))
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_key_does_not_inherit_roles_from_headers(monkeypatch):
    """Un porteur de clé d'API ne doit pas devenir admin via l'en-tête X-Roles."""
    monkeypatch.setenv("API_KEYS", "secret-api-key")
    verifier = ApiToken()

    ctx = verifier(
        make_request(
            {
                "authorization": "Bearer secret-api-key",
                "x-roles": "admin",
            }
        )
    )

    assert ctx.user_id == "api_user"
    assert ctx.roles == []
    assert ctx.is_admin is False


def test_api_key_path_short_circuits_keycloak(keycloak_verifier, monkeypatch):
    def boom(_token):
        raise AssertionError("a valid API key must not reach Keycloak")

    monkeypatch.setattr(keycloak_verifier.keycloak_openid, "introspect", boom)

    ctx = keycloak_verifier(make_request({"authorization": "Bearer secret-api-key", "x-roles": "admin"}))

    assert ctx.user_id == "api_user"
    assert ctx.is_admin is False


def test_unknown_api_key_falls_through_to_keycloak(keycloak_verifier, monkeypatch):
    monkeypatch.setattr(keycloak_verifier.keycloak_openid, "introspect", lambda _token: ACTIVE_CLAIMS)

    ctx = keycloak_verifier(make_request({"authorization": "Bearer not-an-api-key"}))

    assert ctx.user_id == "user-123"
