from celery import Celery

from src.infrastructure.tasks_sender.celery.celery import CeleryTasksSender


def provide_tasks_sender(celery_app: Celery) -> CeleryTasksSender:
    return CeleryTasksSender(celery_app=celery_app)
