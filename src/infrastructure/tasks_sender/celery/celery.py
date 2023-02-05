from celery import Celery

from src.domain.common.interfaces.tasks_sender import TasksSender
from src.domain.menu.dto.menu import OutputMenu


class CeleryTasksSender(TasksSender):
    def __init__(self, celery_app: Celery):
        self.celery = celery_app

    def collect_menu_data(self, menu: OutputMenu) -> str:
        id_ = self.celery.send_task(
            "src.presentation.celery.tasks.collect_menu_data", args=(menu.dict(),)
        )
        return id_.id
