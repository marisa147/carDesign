from typing import TypedDict

from caragent_worker import __version__
from caragent_worker.app import celery_app
from caragent_worker.config import get_settings

GENERATE_2D_CONCEPT_TASK = "caragent_worker.generate_2d_concept_job"
GENERATION_QUEUE = "caragent.default"


class WorkerHealthPayload(TypedDict):
    status: str
    runtime_mode: str
    queue: str
    task_name: str
    worker_version: str
    provider_default: str
    provider_model: str
    provider_calls_enabled: bool
    hosted_provider_configured: bool
    recommended_pool: str


@celery_app.task(name="caragent_worker.worker_health")  # type: ignore[untyped-decorator]
def worker_health() -> WorkerHealthPayload:
    settings = get_settings()
    return {
        "status": "ok",
        "runtime_mode": settings.runtime_mode,
        "queue": GENERATION_QUEUE,
        "task_name": GENERATE_2D_CONCEPT_TASK,
        "worker_version": __version__,
        "provider_default": settings.ai_provider_default,
        "provider_model": settings.ai_provider_model,
        "provider_calls_enabled": settings.ai_provider_calls_enabled,
        "hosted_provider_configured": settings.hosted_provider_configured,
        "recommended_pool": "solo",
    }
