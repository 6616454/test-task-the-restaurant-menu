import asyncio
from typing import Generator, Any

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from src.api.di import setup_di
from src.api.handlers import setup_routes
from src.core.settings import get_settings
from src.infrastructure.db.base import create_pool


def build_test_app() -> FastAPI:
    """Factory test application"""

    settings = get_settings()

    pool = create_pool(database_url=settings.database_test_url, echo_mode=False)

    app = FastAPI(
        title=settings.title
    )

    # setup application
    setup_di(app=app, pool=pool)
    setup_routes(router=app.router)

    return app


@pytest.fixture(scope='session')
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, Any, None]:
    with TestClient(build_test_app()) as client:
        yield client
