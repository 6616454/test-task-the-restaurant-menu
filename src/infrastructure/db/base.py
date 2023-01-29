import logging

from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger('main_logger')

Base = declarative_base()


def create_pool(database_url: str, echo_mode: bool) -> sessionmaker:
    logger.info('Create connections pool for DB')

    engine = create_async_engine(url=database_url, echo=echo_mode, future=True)
    pool = sessionmaker(bind=engine, class_=AsyncSession,
                        expire_on_commit=False, autoflush=False)
    return pool


def create_redis(redis_host: str, redis_port: int, redis_db: int) -> Redis:
    logger.info('Creating Redis...')
    return Redis(host=redis_host, port=redis_port, db=redis_db)
