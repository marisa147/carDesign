from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from kombu.transport import get_transport_cls

from caragent_api import queue


def test_redis_transport_dependency_available_for_celery_queue() -> None:
    transport = get_transport_cls("redis")

    assert transport is not None


def test_celery_queue_client_sends_generation_task_to_worker_queue(
    monkeypatch: Any,
) -> None:
    calls: list[dict[str, Any]] = []

    class FakeResult:
        id = "task-1"

    class FakeCelery:
        def __init__(self, name: str, *, broker: str) -> None:
            calls.append({"broker": broker, "name": name})

        def send_task(self, task_name: str, **kwargs: Any) -> FakeResult:
            calls.append({"kwargs": kwargs, "task_name": task_name})
            return FakeResult()

    monkeypatch.setattr(queue, "Celery", FakeCelery)

    job_id = UUID("11111111-1111-1111-1111-111111111111")
    result = asyncio.run(
        queue.CeleryQueueClient(
            database_url="postgresql+asyncpg://example/db",
            redis_url="redis://localhost:6379/0",
        ).enqueue_generation_job(job_id),
    )

    assert result.job_id == job_id
    assert result.task_id == "task-1"
    assert calls == [
        {"broker": "redis://localhost:6379/0", "name": "caragent_api"},
        {
            "kwargs": {
                "args": [str(job_id)],
                "kwargs": {"database_url": "postgresql+asyncpg://example/db"},
                "queue": "caragent.default",
            },
            "task_name": queue.GENERATE_2D_CONCEPT_TASK,
        },
    ]


def test_celery_queue_client_revokes_known_generation_task(
    monkeypatch: Any,
) -> None:
    calls: list[dict[str, Any]] = []

    class FakeControl:
        def revoke(self, task_id: str, *, terminate: bool) -> None:
            calls.append({"task_id": task_id, "terminate": terminate})

    class FakeCelery:
        def __init__(self, name: str, *, broker: str) -> None:
            calls.append({"broker": broker, "name": name})
            self.control = FakeControl()

    monkeypatch.setattr(queue, "Celery", FakeCelery)

    result = asyncio.run(
        queue.CeleryQueueClient(
            database_url="postgresql+asyncpg://example/db",
            redis_url="redis://localhost:6379/0",
        ).revoke_generation_task("task-1"),
    )

    assert result.status == "revoked"
    assert result.task_id == "task-1"
    assert calls == [
        {"broker": "redis://localhost:6379/0", "name": "caragent_api"},
        {"task_id": "task-1", "terminate": False},
    ]
