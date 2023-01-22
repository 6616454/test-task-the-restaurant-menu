import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger('main_logger')

Base = declarative_base()


def create_pool(database_url: str, echo_mode: bool) -> sessionmaker:
    logger.info('Create connections pool for DB')

    engine = create_async_engine(url=database_url, echo=echo_mode, future=True)
    pool = sessionmaker(bind=engine, class_=AsyncSession,
                        expire_on_commit=False, autoflush=False)
    return pool
