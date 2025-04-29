import redis
from src.config import RedisSettings

redis_settings = RedisSettings()
redis_client = redis.Redis(host=redis_settings.REDIS_HOST, port=redis_settings.REDIS_PORT, db=0)
