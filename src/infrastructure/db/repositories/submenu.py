from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.menu.dto.submenu import CreateSubMenu
from src.infrastructure.db.exception_mapper import exception_mapper
from src.infrastructure.db.models.submenu import SubMenu
from src.infrastructure.db.repositories.base import BaseRepository


class SubMenuRepository(BaseRepository[SubMenu]):
    def __init__(self, session: AsyncSession):
        super().__init__(SubMenu, session)

    async def get_by_id_all(self, id_: str) -> SubMenu:
        query = (
            select(self._model)
            .where(self._model.id == id_)
            .options(joinedload(self._model.dishes))
        )
        result = (await self._session.execute(query)).scalar()
        return result

    async def get_all(self) -> list[SubMenu]:
        query = select(self._model).options(joinedload(self._model.dishes))
        result = (await self._session.execute(query)).scalars().unique()
        return result

    async def get_by_menu_id(self, menu_id: str, load: bool) -> list[SubMenu]:
        query = select(self._model).where(self._model.menu_id == menu_id)
        if load:
            query = query.options(joinedload(self._model.dishes))
            return (await self._session.execute(query)).scalars().unique()
        return (await self._session.execute(query)).scalars().all()

    async def get_by_menu_and_id(
        self, menu_id: str, submenu_id: str, load: bool
    ) -> SubMenu:
        query = select(self._model).where(
            and_(self._model.menu_id == menu_id), self._model.id == submenu_id
        )
        if load:
            query = query.options(joinedload(self._model.dishes))

        result = (await self._session.execute(query)).scalar()
        return result

    @exception_mapper
    async def create_submenu(self, data: CreateSubMenu) -> SubMenu:
        new_submenu = self._model(
            title=data.title, description=data.description, menu_id=data.menu_id
        )

        self._session.add(new_submenu)
        await self._session.flush()

        return new_submenu
