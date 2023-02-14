from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.menu.dto.menu import CreateMenu
from src.infrastructure.db.exception_mapper import exception_mapper
from src.infrastructure.db.models.menu import Menu
from src.infrastructure.db.models.submenu import SubMenu
from src.infrastructure.db.repositories.base import BaseRepository


class MenuRepository(BaseRepository[Menu]):
    def __init__(self, session: AsyncSession):
        super().__init__(Menu, session)

    async def get_all(self) -> list[Menu]:
        query = select(self._model).options(
            joinedload(self._model.submenus).joinedload(SubMenu.dishes)
        )
        result = (await self._session.execute(query)).unique().scalars().all()
        return result

    async def get_by_id_all(self, id_: str, load: bool) -> Menu:
        query = select(self._model).where(self._model.id == id_)
        if load:
            query = query.options(
                joinedload(self._model.submenus).joinedload(SubMenu.dishes)
            )
        result = (await self._session.execute(query)).scalar()
        return result

    async def delete_by_id(self, id_: str) -> None:
        query = delete(self._model).where(self._model.id == id_)
        await self._session.execute(query)

    @exception_mapper
    async def create_menu(self, data: CreateMenu) -> Menu:
        new_menu = self._model(title=data.title, description=data.description)

        self._session.add(new_menu)
        await self._session.flush()

        return new_menu
