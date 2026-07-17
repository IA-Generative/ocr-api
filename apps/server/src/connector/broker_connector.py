from datetime import datetime
from urllib.parse import quote

import redis
from celery import Celery
from redis.exceptions import RedisError
from redis.sentinel import Sentinel

from src.config import CelerySettings, RedisSettings
from src.schemas.health import Health

celery_config = CelerySettings()
redis_settings = RedisSettings()


def _redis_scheme() -> str:
    return "rediss" if redis_settings.REDIS_USE_TLS else "redis"


def _build_redis_url(host: str, port: int, password: str | None) -> str:
    auth = f":{quote(password)}@" if password else ""
    return f"{_redis_scheme()}://{auth}{host}:{port}/{redis_settings.REDIS_DB}"


def _build_broker_url() -> tuple[str, dict]:
    """Build the Celery broker URL and transport options.

    Supports plain redis/rediss, and Sentinel (the actual master is resolved
    at connection time by Celery's own redis-sentinel transport).
    """
    if redis_settings.REDIS_SENTINEL_ENABLED:
        sentinel_scheme = "sentinel"
        password = redis_settings.REDIS_SENTINEL_PASSWORD or redis_settings.REDIS_PASSWORD
        auth = f":{quote(password)}@" if password else ""
        urls = ";".join(
            f"{sentinel_scheme}://{auth}{host}:{port}/{redis_settings.REDIS_DB}"
            for host, port in redis_settings.sentinel_hosts()
        )
        transport_options = {
            "master_name": redis_settings.REDIS_SENTINEL_MASTER_NAME,
            "sentinel_kwargs": (
                {"password": redis_settings.REDIS_SENTINEL_PASSWORD} if redis_settings.REDIS_SENTINEL_PASSWORD else {}
            ),
        }
        return urls, transport_options

    return (
        _build_redis_url(
            redis_settings.REDIS_HOST,
            redis_settings.REDIS_PORT,
            redis_settings.REDIS_PASSWORD,
        ),
        {},
    )


def _build_redis_client() -> redis.Redis:
    """Build a plain redis.Redis client, resolving the current master via Sentinel if enabled."""
    if redis_settings.REDIS_SENTINEL_ENABLED:
        sentinel = Sentinel(
            redis_settings.sentinel_hosts(),
            socket_connect_timeout=2,
            password=redis_settings.REDIS_SENTINEL_PASSWORD,
            ssl=redis_settings.REDIS_USE_TLS,
        )
        return sentinel.master_for(
            redis_settings.REDIS_SENTINEL_MASTER_NAME,
            db=redis_settings.REDIS_DB,
            password=redis_settings.REDIS_PASSWORD,
            ssl=redis_settings.REDIS_USE_TLS,
            socket_connect_timeout=2,
        )

    return redis.Redis(
        host=redis_settings.REDIS_HOST,
        port=redis_settings.REDIS_PORT,
        db=redis_settings.REDIS_DB,
        password=redis_settings.REDIS_PASSWORD,
        ssl=redis_settings.REDIS_USE_TLS,
        socket_connect_timeout=2,
    )


broker_url, broker_transport_options = _build_broker_url()

celery_app = Celery(
    celery_config.CELERY_APP_NAME,
    broker=broker_url,
)
if broker_transport_options:
    celery_app.conf.broker_transport_options = broker_transport_options
    celery_app.conf.result_backend_transport_options = broker_transport_options


class RedisConnector:
    def __init__(self, redis_client: redis.Redis = None):  # type: ignore
        self.client = redis_client or _build_redis_client()
        self.up_time = datetime.now().isoformat()

    def get_health(self):
        try:
            self.client.ping()
        except RedisError as e:
            return Health(
                name="redis",
                extras={"error": str(e)},
                version=redis.__version__,
                up_time=self.up_time,
                status="unhealthy",
            )
        return Health(
            name="redis",
            version=redis.__version__,
            up_time=self.up_time,
            status="healthy",
        )


redis_client = _build_redis_client()
redis_client_connector = RedisConnector(redis_client=redis_client)
