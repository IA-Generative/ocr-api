from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import HTTPException, Response

from ocr_backend.routers import auth as auth_router


def make_request(cookies: dict | None = None):
    header_list = []
    if cookies:
        cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
        header_list.append((b"cookie", cookie_header.encode()))
    scope = {"type": "http", "headers": header_list}
    from fastapi import Request

    return Request(scope)


@pytest.fixture(autouse=True)
def patched_settings(monkeypatch):
    monkeypatch.setattr(auth_router._keycloak_settings, "KEYCLOAK_CLIENT_ID", "ocr")
    monkeypatch.setattr(auth_router._keycloak_settings, "KEYCLOAK_REALM", "mirai")
    monkeypatch.setattr(auth_router._keycloak_settings, "KEYCLOAK_PUBLIC_URL", "http://localhost:8080")
    monkeypatch.setattr(auth_router._keycloak_settings, "BACKEND_PUBLIC_URL", "http://localhost:5000")
    monkeypatch.setattr(auth_router._keycloak_settings, "FRONTEND_URL", "http://localhost:8081")
    monkeypatch.setattr(auth_router._keycloak_settings, "SESSION_COOKIE_NAME", "ocr_session")
    monkeypatch.setattr(auth_router._keycloak_settings, "SESSION_COOKIE_SECURE", False)


@pytest.fixture
def fake_store():
    return Mock()


@pytest.fixture(autouse=True)
def patch_session_store(monkeypatch, fake_store):
    monkeypatch.setattr(auth_router, "_session_store", fake_store)
    return fake_store


@pytest.fixture
def fake_openid():
    return Mock()


@pytest.fixture(autouse=True)
def patch_openid(monkeypatch, fake_openid):
    monkeypatch.setattr(auth_router, "_keycloak_openid", fake_openid)
    return fake_openid


async def test_login_redirects_to_keycloak_with_pkce_and_state(fake_store):
    response = await auth_router.login(redirect="/tasks/42")

    assert response.status_code == 307
    location = urlparse(response.headers["location"])
    assert location.scheme == "http"
    assert location.netloc == "localhost:8080"
    assert location.path == "/realms/mirai/protocol/openid-connect/auth"

    params = parse_qs(location.query)
    assert params["client_id"] == ["ocr"]
    assert params["redirect_uri"] == ["http://localhost:5000/api/auth/callback"]
    assert params["code_challenge_method"] == ["S256"]
    assert "code_challenge" in params
    assert "state" in params

    (state, code_verifier, next_path), _ = fake_store.save_pending.call_args
    assert next_path == "/tasks/42"
    assert state == params["state"][0]


async def test_login_rejects_unsafe_redirect_and_falls_back_to_root(fake_store):
    _ = await auth_router.login(redirect="//evil.tld/phish")

    (_, _, next_path), _ = fake_store.save_pending.call_args
    assert next_path == "/"


async def test_callback_exchanges_code_and_sets_session_cookie(fake_store, fake_openid):
    fake_store.pop_pending.return_value = Mock(code_verifier="verifier-xyz", next_path="/tasks/42")
    fake_openid.token.return_value = {
        "access_token": "tok",
        "refresh_token": "ref",
        "expires_in": 300,
        "refresh_expires_in": 3600,
    }
    fake_openid.introspect.return_value = {
        "sub": "user-123",
        "email": "user@example.com",
        "resource_access": {"ocr": {"roles": ["admin"]}},
    }
    fake_store.create.return_value = "new-session-id"

    response = await auth_router.callback(code="auth-code", state="state-abc", error=None)

    fake_openid.token.assert_called_once_with(
        grant_type="authorization_code",
        code="auth-code",
        redirect_uri="http://localhost:5000/api/auth/callback",
        code_verifier="verifier-xyz",
    )
    assert response.status_code == 302
    assert response.headers["location"] == "http://localhost:8081/tasks/42"
    assert "ocr_session=new-session-id" in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]


async def test_callback_without_code_redirects_without_touching_keycloak(fake_store, fake_openid):
    response = await auth_router.callback(code=None, state=None, error="access_denied")

    fake_openid.token.assert_not_called()
    assert response.status_code == 302
    assert response.headers["location"] == "http://localhost:8081"


async def test_callback_rejects_unknown_state(fake_store, fake_openid):
    fake_store.pop_pending.return_value = None

    response = await auth_router.callback(code="auth-code", state="replayed-state", error=None)

    fake_openid.token.assert_not_called()
    assert response.status_code == 302
    assert "set-cookie" not in response.headers


async def test_logout_revokes_refresh_token_and_clears_cookie(fake_store, fake_openid):
    fake_store.get.return_value = Mock(refresh_token="ref-token")

    response = Response()
    await auth_router.logout(make_request(cookies={"ocr_session": "sid-1"}), response)

    fake_openid.logout.assert_called_once_with("ref-token")
    fake_store.delete.assert_called_once_with("sid-1")
    assert "ocr_session=" in response.headers["set-cookie"]


async def test_logout_without_cookie_is_a_noop(fake_store, fake_openid):
    response = Response()
    await auth_router.logout(make_request(), response)

    fake_store.delete.assert_not_called()
    fake_openid.logout.assert_not_called()


async def test_logout_clears_local_session_even_if_keycloak_revocation_fails(fake_store, fake_openid):
    fake_store.get.return_value = Mock(refresh_token="ref-token")
    fake_openid.logout.side_effect = ConnectionError("keycloak unreachable")

    response = Response()
    await auth_router.logout(make_request(cookies={"ocr_session": "sid-1"}), response)

    fake_store.delete.assert_called_once_with("sid-1")


async def test_me_returns_user_profile_shape(fake_store):
    session = Mock(
        user_id="user-123",
        email="user@example.com",
        first_name="Alice",
        last_name="Martin",
        groups=["ocr-users"],
    )
    fake_store.get.return_value = session
    fake_store.ensure_fresh.return_value = session

    result = await auth_router.me(make_request(cookies={"ocr_session": "sid-1"}))

    assert result == {
        "id": "user-123",
        "email": "user@example.com",
        "firstName": "Alice",
        "lastName": "Martin",
        "groups": ["ocr-users"],
    }


async def test_me_without_session_is_unauthorized(fake_store):
    fake_store.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        await auth_router.me(make_request())
    assert exc.value.status_code == 401
