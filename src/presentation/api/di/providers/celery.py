from celery import Celery

from src.infrastructure.tasks_sender.celery.celery import CeleryTasksSender


def tasks_sender_provider() -> None:
    raise NotImplementedError


def provide_tasks_sender(celery_app: Celery) -> CeleryTasksSender:
    return CeleryTasksSender(celery_app=celery_app)
