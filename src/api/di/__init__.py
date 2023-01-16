from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker

from src.api.di.providers.db import DBProvider, uow_provider
from src.api.di.providers.services import provide_menu_service, menu_service_stub, submenu_service_stub, \
    provide_submenu_service, dish_service_stub, provide_dish_service


def setup_di(app: FastAPI, pool: sessionmaker) -> None:
    db_provider = DBProvider(pool)

    app.dependency_overrides[uow_provider] = db_provider.provide_db
    app.dependency_overrides[menu_service_stub] = lambda: provide_menu_service()
    app.dependency_overrides[submenu_service_stub] = lambda: provide_submenu_service()
    app.dependency_overrides[dish_service_stub] = lambda: provide_dish_service()
