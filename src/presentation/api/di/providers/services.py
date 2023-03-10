from src.domain.common.interfaces.cache import ICache
from src.domain.common.interfaces.tasks_sender import TasksSender
from src.domain.menu.usecases.dish import DishService
from src.domain.menu.usecases.menu import MenuService
from src.domain.menu.usecases.submenu import SubMenuService
from src.domain.report.usecases.report import ReportService
from src.infrastructure.db.uow import SQLAlchemyUoW


def provide_menu_service(uow: SQLAlchemyUoW, cache: ICache) -> MenuService:
    return MenuService(uow=uow, cache=cache)  # type: ignore


def provide_submenu_service(uow: SQLAlchemyUoW, cache: ICache) -> SubMenuService:
    return SubMenuService(uow=uow, cache=cache)  # type: ignore


def provide_dish_service(uow: SQLAlchemyUoW, cache: ICache) -> DishService:
    return DishService(uow=uow, cache=cache)  # type: ignore


def provide_report_service(
    uow: SQLAlchemyUoW, tasks_sender: TasksSender
) -> ReportService:
    return ReportService(uow=uow, tasks_sender=tasks_sender)  # type: ignore
