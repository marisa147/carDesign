from __future__ import annotations

import asyncio
from uuid import UUID

from caragent_core.database import create_engine, create_session_factory, session_scope
from caragent_core.enums import ArtifactKind
from caragent_core.models import Workspace
from caragent_core.services import jobs, workspaces

from caragent_api.config import get_settings


async def run_smoke() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    workspace_id: UUID | None = None

    try:
        async with session_scope(session_factory) as session:
            workspace = await workspaces.create_workspace(
                session,
                title="Phase 2 local smoke",
                owner_id="smoke-local",
            )
            workspace_id = workspace.id
            await workspaces.create_message(
                session,
                workspace.id,
                role="system",
                content="Phase 2 smoke durable message.",
            )
            job_result = await jobs.create_job(
                session,
                workspace.id,
                idempotency_key="phase2-smoke-idempotency-key",
                operation="generate_concept",
                provider="local-simulation",
                model="phase-2-no-provider",
                requested_by="smoke-local",
            )
            await jobs.create_artifact(
                session,
                workspace.id,
                job_id=job_result.job.id,
                object_key=f"smoke/{workspace.id}/preview.txt",
                kind=ArtifactKind.PREVIEW.value,
                content_type="text/plain",
                byte_size=24,
                metadata={"smoke": True},
            )

        async with session_scope(session_factory) as session:
            assert workspace_id is not None
            workspace = await workspaces.get_workspace(session, workspace_id)
            messages = await workspaces.list_messages(session, workspace_id)
            workspace_jobs = await jobs.list_workspace_jobs(session, workspace_id)
            if len(messages) != 1:
                raise RuntimeError(f"Expected 1 smoke message, found {len(messages)}")
            if len(workspace_jobs) != 1:
                raise RuntimeError(f"Expected 1 smoke job, found {len(workspace_jobs)}")

            reused = await jobs.create_job(
                session,
                workspace.id,
                idempotency_key="phase2-smoke-idempotency-key",
                operation="generate_concept",
                requested_by="smoke-local",
            )
            if not reused.idempotent_reused:
                raise RuntimeError("Expected duplicate smoke job request to reuse idempotent job")

            events = await jobs.list_job_events(session, reused.job.id)
            artifacts = await jobs.list_workspace_artifacts(session, workspace.id)
            if not events:
                raise RuntimeError("Expected smoke job to have at least one durable event")
            if len(artifacts) != 1:
                raise RuntimeError(
                    f"Expected 1 smoke artifact metadata row, found {len(artifacts)}",
                )
    finally:
        if workspace_id is not None:
            async with session_scope(session_factory) as session:
                workspace_to_delete = await session.get(Workspace, workspace_id)
                if workspace_to_delete is not None:
                    await session.delete(workspace_to_delete)
        await engine.dispose()


def main() -> None:
    asyncio.run(run_smoke())
    print("Phase 2 durable data smoke passed.")


if __name__ == "__main__":
    main()
