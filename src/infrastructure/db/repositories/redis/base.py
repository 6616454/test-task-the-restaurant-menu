import logging

from redis.asyncio import Redis  # type: ignore

from src.domain.common.interfaces.cache import ICache

logger = logging.getLogger("main_logger")


class RedisRepository(ICache):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def get(self, name: str) -> str:
        return await self._redis.get(name)

    async def put(self, name: str, value: str, expire_at: int | None = None) -> None:
        logger.info("Set new value %s - %s", name, value)

        if expire_at:
            await self._redis.set(name, value, ex=expire_at)
            return

        await self._redis.set(name, value)

    async def delete(self, name: str) -> None:
        logger.info("Delete value - %s", name)
        await self._redis.delete(name)
