import redis
from celery import Celery

from src.config import RedisSettings
from src.config.celery import CelerySettings


celery_config = CelerySettings()
redis_settings = RedisSettings()

celery_app = Celery(
    celery_config.CELERY_APP_NAME,
    broker=f"redis://{redis_settings.REDIS_HOST}:{redis_settings.REDIS_PORT}/",
)

redis_client = redis.Redis(
    host=redis_settings.REDIS_HOST, port=redis_settings.REDIS_PORT, db=0
)
