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
            select(self.model)
            .where(self.model.id == id_)
            .options(joinedload(self.model.dishes))
        )
        result = (await self.session.execute(query)).scalar()
        return result

    async def get_all(self) -> list[SubMenu]:
        query = select(self.model).options(joinedload(self.model.dishes))
        result = (await self.session.execute(query)).scalars().unique()
        return result

    async def get_by_menu_id(self, menu_id: str, load: bool) -> list[SubMenu]:
        query = select(self.model).where(self.model.menu_id == menu_id)
        if load:
            query = query.options(joinedload(self.model.dishes))
            return (await self.session.execute(query)).scalars().unique()
        return (await self.session.execute(query)).scalars().all()

    async def get_by_menu_and_id(
        self, menu_id: str, submenu_id: str, load: bool
    ) -> SubMenu:
        query = select(self.model).where(
            and_(self.model.menu_id == menu_id), self.model.id == submenu_id
        )
        if load:
            query = query.options(joinedload(self.model.dishes))

        result = (await self.session.execute(query)).scalar()
        return result

    @exception_mapper
    async def create_submenu(self, data: CreateSubMenu) -> SubMenu:
        new_submenu = self.model(
            title=data.title, description=data.description, menu_id=data.menu_id
        )

        self.session.add(new_submenu)
        await self.session.flush()

        return new_submenu
