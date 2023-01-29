import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api.di import setup_di
from src.api.handlers import setup_routes
from src.core.logging import setup_logging
from src.core.settings import get_settings
from src.infrastructure.db.base import create_pool, create_redis


def build_app() -> FastAPI:
    """Factory application"""
    setup_logging()

    settings = get_settings()

    pool = create_pool(database_url=settings.database_url,
                       echo_mode=settings.echo_mode)

    app = FastAPI(
        title=settings.title,
        default_response_class=ORJSONResponse
    )

    # setup application
    setup_di(app=app, pool=pool, redis=create_redis(
        settings.redis_host,
        settings.redis_port,
        settings.redis_db
    ))
    setup_routes(router=app.router)

    return app


if __name__ == '__main__':
    uvicorn.run(
        app='src.api.main:build_app',
        factory=True,
        host='0.0.0.0'
    )
