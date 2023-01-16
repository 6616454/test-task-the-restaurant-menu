from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.infrastructure.db.models.submenu import SubMenu
from src.infrastructure.db.repositories.base import BaseRepository


class SubMenuRepository(BaseRepository[SubMenu]):
    def __init__(self, session: AsyncSession):
        super().__init__(SubMenu, session)

    async def get_by_id_all(self, id_: str) -> SubMenu:
        query = select(self.model).where(self.model.id == id_).options(
            joinedload(self.model.dishes)
        )
        result = (await self.session.execute(query)).scalar()
        return result

    async def get_all(self) -> list[SubMenu]:
        query = select(self.model).options(
            joinedload(self.model.dishes)
        )
        result = (await self.session.execute(query)).scalars().unique()
        return result

    async def get_by_menu_id(self, menu_id: str, load=True) -> Optional[list[SubMenu]]:
        query = select(self.model).where(self.model.menu_id == menu_id)
        if load:
            query = query.options(joinedload(self.model.dishes))
            return (await self.session.execute(query)).scalars().unique()
        return (await self.session.execute(query)).scalars().all()

    async def get_by_menu_and_id(self, menu_id: str, submenu_id: str, load=True):
        query = select(self.model).where(and_(self.model.menu_id == menu_id), self.model.id == submenu_id)
        if load:
            query = query.options(joinedload(self.model.dishes))

        result = (await self.session.execute(query)).scalar()
        return result
