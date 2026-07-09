from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_USE_TLS: bool = False

    # Sentinel (optional) — when enabled, REDIS_HOST/REDIS_PORT are ignored and the
    # current master is resolved through the sentinel quorum instead.
    REDIS_SENTINEL_ENABLED: bool = False
    REDIS_SENTINEL_HOSTS: Optional[str] = None  # "host1:26379,host2:26379,host3:26379"
    REDIS_SENTINEL_MASTER_NAME: str = "mymaster"
    REDIS_SENTINEL_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")

    def sentinel_hosts(self) -> list[tuple[str, int]]:
        if not self.REDIS_SENTINEL_HOSTS:
            return []
        hosts: list[tuple[str, int]] = []
        for entry in self.REDIS_SENTINEL_HOSTS.split(","):
            host, _, port = entry.strip().partition(":")
            hosts.append((host, int(port) if port else 26379))
        return hosts
