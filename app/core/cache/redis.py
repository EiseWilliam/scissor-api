from redis.asyncio import Redis
from app.core.config.settings import settings

REDIS_DB = settings.REDIS_URL
redis = Redis(host=REDIS_DB, decode_responses=True)