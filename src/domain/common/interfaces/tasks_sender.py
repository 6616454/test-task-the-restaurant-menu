from typing import Any, Protocol


class TasksSender(Protocol):
    def collect_menu_data(self, menu: list[dict]) -> str:
        pass

    def get_info_by_task_id(self, task_id: str) -> Any:
        pass
