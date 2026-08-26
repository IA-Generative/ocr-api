import time

import pytest


class FakeRedis:
    """Minimal in-memory stand-in for the subset of `redis.Redis` that `SessionStore` uses."""

    def __init__(self):
        self._store: dict[str, tuple[str, float | None]] = {}

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        self._store[key] = (value, time.time() + ttl_seconds)

    def get(self, key: str) -> str | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at is not None and expires_at <= time.time():
            del self._store[key]
            return None
        return value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


@pytest.fixture
def fake_redis() -> FakeRedis:
    return FakeRedis()
