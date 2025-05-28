from datetime import datetime

import redis
from celery import Celery
from redis.exceptions import RedisError

from src.config import CelerySettings, RedisSettings
from src.schemas.health import Health

celery_config = CelerySettings()
redis_settings = RedisSettings()

celery_app = Celery(
    celery_config.CELERY_APP_NAME,
    broker=f"redis://{redis_settings.REDIS_HOST}:{redis_settings.REDIS_PORT}/",
)


class RedisConnector:
    def __init__(self, redis_client: redis.Redis = None):  # type: ignore
        self.client = redis_client or redis.Redis(
            host=redis_settings.REDIS_HOST,
            port=redis_settings.REDIS_PORT,
            db=0,
            socket_connect_timeout=2,
        )
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


redis_client = redis.Redis(
    host=redis_settings.REDIS_HOST, port=redis_settings.REDIS_PORT, db=0
)
redis_client_connector = RedisConnector(redis_client=redis_client)
