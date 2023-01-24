import asyncio
from typing import Generator, Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy import insert, text, delete, select
from sqlalchemy.orm import sessionmaker, close_all_sessions
from httpx import AsyncClient

from src.api.di import setup_di
from src.api.handlers import setup_routes
from src.core.settings import get_settings
from src.infrastructure.db.base import create_pool
from src.infrastructure.db.models.dish import Dish
from src.infrastructure.db.models.menu import Menu
from src.infrastructure.db.models.submenu import SubMenu


def build_test_app() -> FastAPI:
    """Factory test application"""

    settings = get_settings()

    pool = create_pool(database_url=settings.database_test_url, echo_mode=False)

    app = FastAPI(
        title=settings.title
    )

    # setup test application
    setup_di(app=app, pool=pool)
    setup_routes(router=app.router)

    return app


@pytest.fixture(scope='session')
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def client() -> Generator[AsyncClient, Any, None]:
    async with AsyncClient(app=build_test_app(), base_url='http://test') as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def db_session_test() -> sessionmaker:
    yield create_pool(get_settings().database_test_url, echo_mode=False)
    close_all_sessions()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_tables(db_session_test):
    tables = ('menu', 'submenu', 'dish')
    async with db_session_test() as session:
        for table in tables:
            statement = text(f'''TRUNCATE TABLE {table} CASCADE;''')
            await session.execute(statement)
            await session.commit()


@pytest_asyncio.fixture(scope='function')
async def create_menu_in_database(db_session_test: sessionmaker):
    async def create_menu_in_database(menu_id: str, title: str, description: str):
        async with db_session_test() as session:
            await session.execute(insert(Menu).values(id=menu_id, title=title, description=description))
            await session.commit()

    return create_menu_in_database


@pytest_asyncio.fixture(scope='function')
async def create_submenu_in_database(db_session_test: sessionmaker):
    async def create_submenu_in_database(submenu_id: str, title: str, description: str, menu_id: str):
        async with db_session_test() as session:
            await session.execute(insert(SubMenu).values(
                id=submenu_id,
                title=title,
                description=description,
                menu_id=menu_id
            ))
            await session.commit()

    return create_submenu_in_database


@pytest_asyncio.fixture(scope='function')
async def create_dish_in_database(db_session_test: sessionmaker):
    async def create_dish_in_database(
            dish_id: str,
            title: str,
            description: str,
            price: str,
            submenu_id: str
    ):
        async with db_session_test() as session:
            await session.execute(insert(Dish).values(
                id=dish_id,
                title=title,
                description=description,
                price=price,
                submenu_id=submenu_id
            ))
            await session.commit()

    return create_dish_in_database


@pytest_asyncio.fixture(scope='function')
async def delete_menu_from_database(db_session_test: sessionmaker):
    async def delete_menu_from_database(menu_id: str):
        async with db_session_test() as session:
            query = delete(Menu).where(Menu.id == menu_id)
            await session.execute(query)
            await session.commit()

    return delete_menu_from_database


@pytest_asyncio.fixture(scope='function')
async def delete_submenu_from_database(db_session_test: sessionmaker):
    async def delete_submenu_from_database(submenu_id: str):
        async with db_session_test() as session:
            query = delete(SubMenu).where(SubMenu.id == submenu_id)
            await session.execute(query)
            await session.commit()

    return delete_submenu_from_database


@pytest_asyncio.fixture(scope='function')
async def delete_dish_from_database(db_session_test: sessionmaker):
    async def delete_dish_from_database(dish_id: str):
        async with db_session_test() as session:
            query = delete(Dish).where(Dish.id == dish_id)
            await session.execute(query)
            await session.commit()

    return delete_dish_from_database


@pytest_asyncio.fixture(scope='function')
async def get_menu_from_database(db_session_test: sessionmaker):
    async def get_menu_from_database(menu_id: str):
        async with db_session_test() as session:
            query = select(Menu).where(Menu.id == menu_id)
            return (await session.execute(query)).scalar_one_or_none()

    return get_menu_from_database


@pytest_asyncio.fixture(scope='function')
async def get_submenu_from_database(db_session_test: sessionmaker):
    async def get_submenu_from_database(submenu_id: str):
        async with db_session_test() as session:
            query = select(SubMenu).where(SubMenu.id == submenu_id)
            return (await session.execute(query)).scalar_one_or_none()

    return get_submenu_from_database


@pytest_asyncio.fixture(scope='function')
async def get_dish_from_database(db_session_test: sessionmaker):
    async def get_submenu_from_database(dish_id: str):
        async with db_session_test() as session:
            query = select(Dish).where(Dish.id == dish_id)
            return (await session.execute(query)).scalar_one_or_none()

    return get_submenu_from_database


@pytest.fixture(scope='function')
def menu_data():
    return {
        'menu_id': 'b61ec7b4-5b25-41de-9d41-f00331b04885',
        'title': 'some_title',
        'description': 'some_description',
    }


@pytest.fixture
def submenu_data():
    return {
        'submenu_id': '5f740121-65d6-490b-984c-1cb28a4b43fa',
        'title': 'some_title',
        'description': 'some_description',
        'menu_id': 'b61ec7b4-5b25-41de-9d41-f00331b04885',
    }


@pytest.fixture
def dish_data():
    return {
        'dish_id': '911577a1-fbf5-4931-b075-e7641c84121a',
        'title': 'some_title',
        'description': 'some_description',
        'price': '14.50',
        'submenu_id': '5f740121-65d6-490b-984c-1cb28a4b43fa',
    }
