from redis.asyncio import Redis
from app.core.config.settings import settings

REDIS_HOST = settings.REDIS_HOST

redis = Redis(host=REDIS_HOST, decode_responses=True)