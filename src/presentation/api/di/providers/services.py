from src.domain.menu.usecases.dish import DishService
from src.domain.menu.usecases.menu import MenuService
from src.domain.menu.usecases.submenu import SubMenuService


def menu_service_stub() -> None:
    raise NotImplementedError


def submenu_service_stub() -> None:
    raise NotImplementedError


def dish_service_stub() -> None:
    raise NotImplementedError


def provide_menu_service() -> MenuService:
    return MenuService()


def provide_submenu_service() -> SubMenuService:
    return SubMenuService()


def provide_dish_service() -> DishService:
    return DishService()
