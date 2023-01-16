from asyncio import Protocol


class IBaseUoW(Protocol):
    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass
