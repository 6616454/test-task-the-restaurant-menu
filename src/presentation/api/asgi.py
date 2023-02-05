import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.infrastructure.db.base import create_pool, create_redis
from src.logging import setup_logging
from src.presentation.api.di import setup_di
from src.presentation.api.handlers import setup_routes
from src.settings import get_settings


def build_app() -> FastAPI:
    """Factory application"""
    setup_logging()

    settings = get_settings()

    pool = create_pool(database_url=settings.database_url, echo_mode=settings.echo_mode)

    app = FastAPI(title=settings.title, default_response_class=ORJSONResponse)

    # setup application
    setup_di(
        app=app,
        pool=pool,
        redis=create_redis(
            redis_host=settings.redis_host,
            redis_port=settings.redis_port,
            redis_db=settings.redis_db,
        ),
    )
    setup_routes(router=app.router)

    return app


if __name__ == "__main__":
    uvicorn.run(app="src.presentation.api.asgi:build_app", factory=True, host="0.0.0.0")
