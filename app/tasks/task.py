import time

from app.configs.celery_app import celery_app


@celery_app.task()
def call_background_task(message: str) -> None:
    time.sleep(10)
    print("Background Task called!")
    print(message)
