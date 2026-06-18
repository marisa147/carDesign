from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from celery import Celery

GENERATE_2D_CONCEPT_TASK = "caragent_worker.generate_2d_concept_job"
GENERATION_QUEUE = "caragent.default"


@dataclass(frozen=True, slots=True)
class QueuedGenerationTask:
    job_id: UUID
    task_id: str | None
    task_name: str


@dataclass(frozen=True, slots=True)
class QueueInspection:
    status: str
    generation_queue: str
    active_workers: int
    registered_tasks: list[str]
    active_tasks: int
    reserved_tasks: int
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class QueueRevokeResult:
    status: str
    task_id: str | None
    detail: str | None = None


class QueueClient(Protocol):
    async def enqueue_generation_job(self, job_id: UUID) -> QueuedGenerationTask:
        """Enqueue the worker-owned generation task by job id."""

    async def inspect_generation_queue(self) -> QueueInspection:
        """Best-effort inspection of registered workers and queued/running tasks."""

    async def revoke_generation_task(self, task_id: str | None) -> QueueRevokeResult:
        """Best-effort revoke for a known generation task id."""


class CeleryQueueClient:
    def __init__(self, *, database_url: str | None, redis_url: str) -> None:
        self._database_url = database_url
        self._redis_url = redis_url

    async def enqueue_generation_job(self, job_id: UUID) -> QueuedGenerationTask:
        celery_app = Celery("caragent_api", broker=self._redis_url)
        result = celery_app.send_task(
            GENERATE_2D_CONCEPT_TASK,
            args=[str(job_id)],
            kwargs={"database_url": self._database_url} if self._database_url else {},
            queue=GENERATION_QUEUE,
        )
        return QueuedGenerationTask(
            job_id=job_id,
            task_id=result.id,
            task_name=GENERATE_2D_CONCEPT_TASK,
        )

    async def inspect_generation_queue(self) -> QueueInspection:
        celery_app = Celery("caragent_api", broker=self._redis_url)
        inspector = celery_app.control.inspect(timeout=1.0)
        ping = inspector.ping() or {}
        registered = inspector.registered() or {}
        active = inspector.active() or {}
        reserved = inspector.reserved() or {}
        active_workers = len(ping) if isinstance(ping, dict) else 0
        registered_tasks = sorted(
            {
                str(task_name)
                for task_names in registered.values()
                if isinstance(task_names, list)
                for task_name in task_names
            },
        )
        status = "ok" if active_workers > 0 else "unavailable"
        detail = None if active_workers > 0 else "No worker replied to Celery inspect."
        return QueueInspection(
            active_tasks=_count_task_payload(active),
            active_workers=active_workers,
            detail=detail,
            generation_queue=GENERATION_QUEUE,
            registered_tasks=registered_tasks,
            reserved_tasks=_count_task_payload(reserved),
            status=status,
        )

    async def revoke_generation_task(self, task_id: str | None) -> QueueRevokeResult:
        if not task_id:
            return QueueRevokeResult(
                detail="No Celery task id is available for this job.",
                status="not_available",
                task_id=None,
            )

        celery_app = Celery("caragent_api", broker=self._redis_url)
        try:
            celery_app.control.revoke(task_id, terminate=False)
        except Exception:  # pragma: no cover - broker failures are environment dependent
            return QueueRevokeResult(
                detail="Celery revoke failed.",
                status="failed",
                task_id=task_id,
            )
        return QueueRevokeResult(detail=None, status="revoked", task_id=task_id)


def _count_task_payload(payload: object) -> int:
    if not isinstance(payload, dict):
        return 0
    total = 0
    for task_list in payload.values():
        if isinstance(task_list, list):
            total += len(task_list)
    return total
