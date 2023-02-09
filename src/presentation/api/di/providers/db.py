from sqlalchemy.orm import sessionmaker

from src.infrastructure.db.uow import SQLAlchemyUoW


def uow_provider() -> None:
    raise NotImplementedError


class DBProvider:
    def __init__(self, pool: sessionmaker):
        self.pool = pool

    async def provide_db(self):
        async with self.pool() as session:
            yield SQLAlchemyUoW(session)
