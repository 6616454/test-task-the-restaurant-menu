import logging
from collections.abc import Callable

from celery import Celery

from src.presentation.celery.tasks import collect_menu_data
from src.settings import get_settings

logger = logging.getLogger("main_logger")


def build_celery_app() -> Celery:
    """Factory celery application"""
    logger.info("Celery app creating...")

    settings = get_settings()

    celery_app = Celery(main="name", broker=settings.broker_url, backend="rpc://")

    # Inject tasks to app
    celery_app.task(collect_menu_data)

    return celery_app


def _inject_dependency_to_task(task: Callable, **depends) -> Callable:
    """Special func for inject your own dependencies to task"""

    task_provider = lambda: task(**depends)  # noqa
    task_provider.__name__ = task.__name__
    return task_provider


app = build_celery_app()
