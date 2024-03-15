from celery import Celery
from app.core.config.settings import settings

BROKER = settings.CELERY_BROKER_URL
BACKEND = settings.CELERY_RESULT_BACKEND


def make_celery(app_name=__name__):
    backend = BACKEND
    broker = BROKER
    return Celery(app_name, backend=backend, broker=broker, broker_connection_retry_on_startup=True)


celery_app = make_celery()
