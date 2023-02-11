from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.menu.dto.dish import CreateDish
from src.infrastructure.db.exception_mapper import exception_mapper
from src.infrastructure.db.models.dish import Dish
from src.infrastructure.db.repositories.base import BaseRepository


class DishRepository(BaseRepository[Dish]):
    def __init__(self, session: AsyncSession):
        super().__init__(Dish, session)

    async def get_by_submenu(self, submenu_id: str) -> list[Dish]:
        query = select(self.model).where(self.model.submenu_id == submenu_id)
        return (await self.session.execute(query)).scalars().all()

    async def get_by_submenu_and_id(self, submenu_id: str, dish_id: str) -> Dish:
        query = select(self.model).where(
            and_(self.model.id == dish_id, self.model.submenu_id == submenu_id)
        )
        return (await self.session.execute(query)).scalar()

    @exception_mapper
    async def create_dish(self, dish: CreateDish) -> Dish:
        new_dish = self.model(
            title=dish.title,
            description=dish.description,
            price=dish.price,
            submenu_id=dish.submenu_id,
        )
        await self.save(new_dish)
        await self.session.flush()

        return new_dish
