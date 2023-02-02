from fastapi import APIRouter

from src.presentation.api.handlers.menu.menu import router as menu_router
from src.presentation.api.handlers.menu.submenu import router as sub_menu_router
from src.presentation.api.handlers.menu.dish import router as dish_router


def setup_routes(router: APIRouter):
    router.include_router(menu_router)
    router.include_router(sub_menu_router)
    router.include_router(dish_router)
