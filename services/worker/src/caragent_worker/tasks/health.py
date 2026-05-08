from typing import TypedDict

from caragent_worker.app import celery_app
from caragent_worker.config import get_settings


class WorkerHealthPayload(TypedDict):
    status: str
    runtime_mode: str
    queue: str
    external_calls: bool


@celery_app.task(name="caragent_worker.worker_health")  # type: ignore[misc]
def worker_health() -> WorkerHealthPayload:
    settings = get_settings()
    return {
        "status": "ok",
        "runtime_mode": settings.runtime_mode,
        "queue": "redis",
        "external_calls": False,
    }
