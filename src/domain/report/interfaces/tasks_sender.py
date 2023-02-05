from typing import Protocol

from src.domain.menu.dto.menu import OutputMenu


class IReportTasksSender(Protocol):
    def collect_menu_data(self, menu: OutputMenu) -> str:
        pass
