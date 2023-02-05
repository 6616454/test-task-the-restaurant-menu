from typing import Protocol

from src.infrastructure.db.uow import MenuHolder


class IReportUoW(Protocol):
    menu_holder: MenuHolder
