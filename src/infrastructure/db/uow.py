from redis.asyncio.client import Redis  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.interfaces.uow import IBaseUoW
from src.infrastructure.db.repositories.dish import DishRepository
from src.infrastructure.db.repositories.menu import MenuRepository
from src.infrastructure.db.repositories.redis.base import RedisRepository
from src.infrastructure.db.repositories.submenu import SubMenuRepository


class SQLAlchemyBaseUoW(IBaseUoW):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()


class MenuHolder:
    def __init__(self, session: AsyncSession):
        self.menu_repo = MenuRepository(session)
        self.submenu_repo = SubMenuRepository(session)
        self.dish_repo = DishRepository(session)


class SQLAlchemyUoW(SQLAlchemyBaseUoW):
    def __init__(self, session: AsyncSession, redis: Redis):
        super().__init__(session)

        self.menu_holder = MenuHolder(session)
        self.redis_repo = RedisRepository(redis)
