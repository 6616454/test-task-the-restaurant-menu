import uvicorn
from fastapi import FastAPI

from src.api.di import setup_di
from src.api.handlers import setup_routes
from src.core.logging import setup_logging
from src.core.settings import get_settings
from src.infrastructure.db.base import create_pool


def build_app() -> FastAPI:
    """Factory application"""
    setup_logging()

    settings = get_settings()

    pool = create_pool(database_url=settings.database_url, echo_mode=settings.echo_mode)

    app = FastAPI(
        title=settings.title
    )

    # setup application
    setup_di(app=app, pool=pool)
    setup_routes(router=app.router)

    return app


if __name__ == '__main__':
    uvicorn.run(
        app='src.api.main:build_app',
        factory=True,
        host='0.0.0.0'
    )
