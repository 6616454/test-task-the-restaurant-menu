from fastapi import FastAPI, Depends
from redis.asyncio.client import Redis  # type: ignore
from sqlalchemy.orm import sessionmaker

from src.infrastructure.db.uow import SQLAlchemyUoW
from src.presentation.api.di.providers.celery import provide_tasks_sender
from src.presentation.api.di.providers.db import DBProvider, uow_provider
from src.presentation.api.di.providers.services import (
    provide_menu_service,
    provide_submenu_service,
    provide_dish_service,
    report_service_stub,
    provide_report_service,
)
from src.presentation.celery.app import app as celery_app


def setup_di(app: FastAPI, pool: sessionmaker, redis: Redis) -> None:
    db_provider = DBProvider(pool, redis)

    app.dependency_overrides[uow_provider] = db_provider.provide_db
    app.dependency_overrides[report_service_stub] = lambda: provide_report_service(
        tasks_sender=provide_tasks_sender(celery_app=celery_app)
    )


def get_menu_service(uow: SQLAlchemyUoW = Depends(uow_provider)):
    return provide_menu_service(uow)


def get_submenu_service(uow: SQLAlchemyUoW = Depends(uow_provider)):
    return provide_submenu_service(uow)


def get_dish_service(uow: SQLAlchemyUoW = Depends(uow_provider)):
    return provide_dish_service(uow)
