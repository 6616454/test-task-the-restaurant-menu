from redis.asyncio.client import Redis

from src.infrastructure.db.repositories.redis.base import RedisRepository


def redis_provider() -> None:
    raise NotImplementedError


class CacheProvider:
    def __init__(self, redis: Redis):
        self.redis = redis

    def provide_redis(self):
        return RedisRepository(self.redis)
