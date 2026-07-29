import os
import time

import httpx
import pytest

# test_models.py imports apps/server's src.schemas to diff it against ocr_sdk's
# schemas — that pulls in src.connector.db_connector at import time, which now
# refuses to start without a real DATABASE_URL unless explicitly opted out.
# These tests never touch the DB, so opt into the local SQLite fallback here.
os.environ.setdefault("ALLOW_SQLITE_FALLBACK", "1")

API_BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def api_ready():
    """Block until the API serves a healthy response.

    `docker compose up -d` returns as soon as containers are created, not when
    the API is accepting requests, so tests that hit it immediately can fail
    with connection resets. Polling /api/health (which is 200 only when db,
    redis and minio are all healthy) lets the tests wait for a real readiness
    signal instead.
    """

    deadline = time.monotonic() + 90
    last = None

    while time.monotonic() < deadline:
        try:
            r = httpx.get(f"{API_BASE_URL}/api/health", timeout=5.0)

            if r.status_code == 200 and r.json().get("status") == "healthy":
                return

            last = f"status={r.status_code} body={r.text[:200]}"

        except httpx.TransportError as exc:
            last = repr(exc)

        time.sleep(2)

    pytest.fail(f"API at {API_BASE_URL} not healthy within 90s. Last: {last}")
