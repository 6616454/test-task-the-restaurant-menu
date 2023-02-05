from src.domain.common.interfaces.tasks_sender import TasksSender
from src.domain.menu.usecases.dish import DishService
from src.domain.menu.usecases.menu import MenuService
from src.domain.menu.usecases.submenu import SubMenuService
from src.domain.report.usecases.report import ReportService


def menu_service_stub() -> None:
    raise NotImplementedError


def submenu_service_stub() -> None:
    raise NotImplementedError


def dish_service_stub() -> None:
    raise NotImplementedError


def report_service_stub() -> None:
    raise NotImplementedError


def provide_menu_service() -> MenuService:
    return MenuService()


def provide_submenu_service() -> SubMenuService:
    return SubMenuService()


def provide_dish_service() -> DishService:
    return DishService()


def provide_report_service(tasks_sender: TasksSender) -> ReportService:
    return ReportService(tasks_sender)
