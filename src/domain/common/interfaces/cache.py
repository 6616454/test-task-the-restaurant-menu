from typing import Protocol


class ICache(Protocol):
    async def get(self, value: str) -> str | None:
        pass

    async def put(self, name: str, value: str, expire_at: int | None = None) -> None:
        pass

    async def delete(self, name: str) -> None:
        pass
