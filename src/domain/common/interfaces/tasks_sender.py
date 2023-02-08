from abc import ABC, abstractmethod
from typing import Any


class TasksSender(ABC):
    @abstractmethod
    def collect_menu_data(self, menu: list[dict]) -> str:
        pass

    @abstractmethod
    def get_info_by_task_id(self, task_id: str) -> Any:
        pass
