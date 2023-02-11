from typing import Generic, TypeVar

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.base import Base
from src.infrastructure.db.exception_mapper import exception_mapper

Model = TypeVar("Model", bound=Base)


class BaseRepository(Generic[Model]):
    def __init__(self, model: type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id_: str) -> Model:
        query = select(self.model).where(self.model.id == id_)
        return (await self.session.execute(query)).scalar_one_or_none()

    async def get_all(self) -> list[Model]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    @exception_mapper
    async def update_obj(self, id_: str, **kwargs) -> None:
        query = update(self.model).where(self.model.id == id_).values(kwargs)
        await self.session.execute(query)

    async def delete(self, obj: Model) -> None:
        await self.session.delete(obj)
