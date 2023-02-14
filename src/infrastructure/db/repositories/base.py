from typing import Generic, TypeVar

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.base import Base
from src.infrastructure.db.exception_mapper import exception_mapper

Model = TypeVar("Model", bound=Base)


class BaseRepository(Generic[Model]):
    def __init__(self, model: type[Model], session: AsyncSession):
        self._model = model
        self._session = session

    async def get_by_id(self, id_: str) -> Model:
        query = select(self._model).where(self._model.id == id_)
        return (await self._session.execute(query)).scalar_one_or_none()

    async def get_all(self) -> list[Model]:
        result = await self._session.execute(select(self._model))
        return result.scalars().all()

    @exception_mapper
    async def update_obj(self, id_: str, **kwargs) -> None:
        query = update(self._model).where(self._model.id == id_).values(kwargs)
        await self._session.execute(query)

    async def delete(self, obj: Model) -> None:
        await self._session.delete(obj)

    async def save(self, obj: Model) -> None:
        self._session.add(obj)
