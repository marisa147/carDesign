from celery import Celery

from caragent_worker.config import get_settings

settings = get_settings()

celery_app = Celery(
    "caragent_worker",
    broker=settings.redis_url,
    include=["caragent_worker.tasks.health"],
)

celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    result_backend=None,
    task_default_queue="caragent.default",
    task_track_started=True,
    worker_hijack_root_logger=False,
)
