from celery import Celery


celery_app = Celery(
    __name__,
    broker="redis://:aSDj1k2n!ewmdk@127.0.0.1:6379/0",
    backend="redis://:aSDj1k2n!ewmdk@127.0.0.1:6379/0",
    broker_connection_retry_on_startup=True,
)

celery_app.autodiscover_tasks(["app.tasks"])


celery_app.conf.beat_schedule = {
    "run-me-background-task": {
        "task": "app.tasks.task.call_background_task",
        "schedule": 60.0,
        "args": ("Test text message",),
    }
}
