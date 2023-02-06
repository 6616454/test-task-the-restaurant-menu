from typing import Protocol


class IReportTasksSender(Protocol):
    def collect_menu_data(self, menu: list[dict]) -> str:
        pass
