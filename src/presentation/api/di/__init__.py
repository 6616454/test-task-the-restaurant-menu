from fastapi import FastAPI, Depends
from redis.asyncio.client import Redis  # type: ignore
from sqlalchemy.orm import sessionmaker

from src.domain.common.interfaces.tasks_sender import TasksSender
from src.infrastructure.db.uow import SQLAlchemyUoW
from src.presentation.api.di.providers.celery import (
    provide_tasks_sender,
    tasks_sender_stub,
)
from src.presentation.api.di.providers.db import DBProvider, uow_provider
from src.presentation.api.di.providers.services import (
    provide_menu_service,
    provide_submenu_service,
    provide_dish_service,
    provide_report_service,
)
from src.presentation.celery.app import app as celery_app


def setup_di(app: FastAPI, pool: sessionmaker, redis: Redis) -> None:
    db_provider = DBProvider(pool, redis)

    app.dependency_overrides[tasks_sender_stub] = lambda: provide_tasks_sender(
        celery_app=celery_app
    )
    app.dependency_overrides[uow_provider] = db_provider.provide_db


def get_menu_service(uow: SQLAlchemyUoW = Depends(uow_provider)):
    return provide_menu_service(uow=uow)


def get_submenu_service(uow: SQLAlchemyUoW = Depends(uow_provider)):
    return provide_submenu_service(uow=uow)


def get_dish_service(uow: SQLAlchemyUoW = Depends(uow_provider)):
    return provide_dish_service(uow=uow)


def get_report_service(
    uow: SQLAlchemyUoW = Depends(uow_provider),
    tasks_sender: TasksSender = Depends(tasks_sender_stub),
):
    return provide_report_service(uow=uow, tasks_sender=tasks_sender)
