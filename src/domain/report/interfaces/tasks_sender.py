from typing import Protocol

from celery.backends.database import Task


class IReportTasksSender(Protocol):
    def collect_menu_data(self, menu: list[dict]) -> str:
        pass

    def get_info_by_task_id(self, task_id: str) -> Task:
        pass
