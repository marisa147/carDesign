from __future__ import annotations

import asyncio
from collections.abc import Iterator
from pathlib import Path
from uuid import UUID

import pytest
from caragent_core.database import create_engine, create_session_factory, session_scope
from caragent_core.enums import JobStatus, ModelRunStatus
from caragent_core.models import GenerationJob, JobEvent, ModelRun, metadata
from caragent_core.services import jobs, workspaces
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from caragent_worker.tasks.jobs import simulate_local_generation_job


@pytest.fixture
def seeded_job(
    tmp_path: Path,
) -> Iterator[tuple[str, async_sessionmaker[AsyncSession], UUID]]:
    database_url = f"sqlite+aiosqlite:///{(tmp_path / 'worker-jobs.db').as_posix()}"
    engine = create_engine(database_url)
    session_factory = create_session_factory(engine)
    job_id = asyncio.run(seed_database(engine, session_factory))

    yield database_url, session_factory, job_id

    asyncio.run(engine.dispose())


async def seed_database(
    engine: AsyncEngine,
    session_factory: async_sessionmaker[AsyncSession],
) -> UUID:
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)

    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Worker")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="worker-001",
            operation="generate_concept",
        )

    return created.job.id


def test_local_simulation_task_updates_durable_job_state(
    seeded_job: tuple[str, async_sessionmaker[AsyncSession], UUID],
) -> None:
    database_url, session_factory, job_id = seeded_job

    result = simulate_local_generation_job.run(str(job_id), database_url=database_url)

    job, events, model_runs = asyncio.run(read_job_state(session_factory, job_id))

    assert result == {
        "external_calls": False,
        "job_id": str(job_id),
        "model": "phase-2-no-provider",
        "provider": "local-simulation",
        "status": "succeeded",
    }
    assert job.status == JobStatus.SUCCEEDED.value
    assert job.estimated_cost == 0
    assert job.actual_cost == 0
    assert [event.status for event in events] == ["queued", "running", "succeeded"]
    assert [event.source for event in events] == [
        "api",
        "worker-local-simulation",
        "worker-local-simulation",
    ]
    assert len(model_runs) == 1
    assert model_runs[0].provider == "local-simulation"
    assert model_runs[0].model == "phase-2-no-provider"
    assert model_runs[0].status == ModelRunStatus.SUCCEEDED.value
    assert model_runs[0].estimated_cost == 0
    assert model_runs[0].actual_cost == 0


def test_local_simulation_task_records_failed_state(
    seeded_job: tuple[str, async_sessionmaker[AsyncSession], UUID],
) -> None:
    database_url, session_factory, job_id = seeded_job

    result = simulate_local_generation_job.run(
        str(job_id),
        database_url=database_url,
        force_error_message="provider secret\nfailed",
    )

    job, events, _model_runs = asyncio.run(read_job_state(session_factory, job_id))

    assert result["status"] == "failed"
    assert job.status == JobStatus.FAILED.value
    assert job.latest_error == "provider secret failed"
    assert [event.status for event in events] == ["queued", "running", "failed"]
    assert events[-1].event_type == "error"
    assert events[-1].source == "worker-local-simulation"


def test_local_simulation_task_rejects_missing_database_url() -> None:
    with pytest.raises(RuntimeError, match="DATABASE_URL is required"):
        simulate_local_generation_job.run("00000000-0000-0000-0000-000000000000")


async def read_job_state(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: UUID,
) -> tuple[GenerationJob, list[JobEvent], list[ModelRun]]:
    async with session_scope(session_factory) as session:
        job = await jobs.get_job(session, job_id)
        events = await jobs.list_job_events(session, job_id)
        model_runs = await jobs.list_job_model_runs(session, job_id)
    return job, events, model_runs
