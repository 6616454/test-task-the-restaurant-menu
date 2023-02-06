from src.domain.common.interfaces.tasks_sender import TasksSender
from src.domain.menu.usecases.dish import DishService
from src.domain.menu.usecases.menu import MenuService
from src.domain.menu.usecases.submenu import SubMenuService
from src.domain.report.usecases.report import ReportService
from src.infrastructure.db.uow import SQLAlchemyUoW


def report_service_stub() -> None:
    raise NotImplementedError


def provide_menu_service(uow: SQLAlchemyUoW) -> MenuService:
    return MenuService(uow=uow)  # type: ignore


def provide_submenu_service(uow: SQLAlchemyUoW) -> SubMenuService:
    return SubMenuService(uow=uow)  # type: ignore


def provide_dish_service(uow: SQLAlchemyUoW) -> DishService:
    return DishService(uow=uow)  # type: ignore


def provide_report_service(tasks_sender: TasksSender) -> ReportService:
    return ReportService(tasks_sender)
