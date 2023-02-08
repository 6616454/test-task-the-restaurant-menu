import logging

from celery import Celery
from celery.backends.database import Task

from src.domain.common.interfaces.tasks_sender import TasksSender

logger = logging.getLogger("main_logger")


class CeleryTasksSender(TasksSender):
    def __init__(self, celery_app: Celery):
        self.celery = celery_app

    def collect_menu_data(self, report_menus: list[dict]) -> str:
        logger.info("Report to EXCEL task started...")

        new_task = self.celery.send_task(
            "src.presentation.celery.tasks.collect_menu_data", args=(report_menus,)
        )

        return new_task.id

    def get_info_by_task_id(self, task_id: str) -> Task:
        return self.celery.AsyncResult(task_id)
