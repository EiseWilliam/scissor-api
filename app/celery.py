from celery import Celery


def make_celery(app_name=__name__):
    broker="redis://127.0.0.1:6379/0"
    backend="redis://127.0.0.1:6379/0"
    return Celery(app_name, backend=backend, broker=broker, broker_connection_retry_on_startup=True)

celery_app = make_celery()