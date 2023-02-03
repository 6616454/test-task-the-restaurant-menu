from abc import ABC, abstractmethod


class ICache(ABC):
    @abstractmethod
    async def get(self, value: str) -> str | None:
        pass

    @abstractmethod
    async def put(self, name: str, value: str, expire_at: int | None = None) -> None:
        pass

    @abstractmethod
    async def delete(self, name: str) -> None:
        pass
