from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.dish import Dish
from src.infrastructure.db.repositories.base import BaseRepository


class DishRepository(BaseRepository[Dish]):
    def __init__(self, session: AsyncSession):
        super().__init__(Dish, session)

    async def get_by_submenu(self, submenu_id: str):
        query = select(self.model).where(self.model.submenu_id == submenu_id)
        return (await self.session.execute(query)).scalars().all()

    async def get_by_submenu_and_id(self, submenu_id, dish_id):
        query = select(self.model).where(and_(self.model.id == dish_id, self.model.submenu_id == submenu_id))
        return (await self.session.execute(query)).scalar()
