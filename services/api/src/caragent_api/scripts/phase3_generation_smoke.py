from __future__ import annotations

import asyncio
import base64
import hashlib
import shutil
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

from caragent_core.database import create_engine, create_session_factory, session_scope
from caragent_core.enums import (
    ArtifactKind,
    DesignVersionStatus,
    JobEventType,
    JobStatus,
    ModelRunStatus,
)
from caragent_core.generation import (
    PromptProviderSettings,
    build_prompt_plan,
    create_generation_brief,
)
from caragent_core.models import Workspace
from caragent_core.services import jobs, workspaces
from caragent_core.storage import FileObjectStorage, build_object_key

from caragent_api.config import get_settings

PNG_1X1_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/"
    "l1m6dQAAAABJRU5ErkJggg==",
)
SMOKE_STORAGE_ROOT = Path(".caragent-smoke")


async def run_smoke() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    storage = FileObjectStorage(root=SMOKE_STORAGE_ROOT)
    workspace_id: UUID | None = None

    try:
        async with session_scope(session_factory) as session:
            workspace = await workspaces.create_workspace(
                session,
                title="Phase 3 local generation smoke",
                owner_id="smoke-local",
            )
            workspace_id = workspace.id
            message = await workspaces.create_message(
                session,
                workspace.id,
                role="user",
                content=(
                    "白色双门车，樱色女主角，车门文字 MOON DRIVE，"
                    "整体偏清爽赛博风。"
                ),
            )
            brief_payload = create_generation_brief(
                original_request=message.content,
                character_theme="Sakura heroine",
                palette=["white", "teal"],
                style="itasha concept",
                text=["MOON DRIVE"],
            )
            brief = await workspaces.create_design_brief(
                session,
                workspace.id,
                payload=brief_payload.model_dump(mode="json"),
                source_message_id=message.id,
                title="Phase 3 smoke brief",
            )
            job_result = await jobs.create_job(
                session,
                workspace.id,
                brief_id=brief.id,
                idempotency_key="phase3-smoke-idempotency-key",
                operation="generate_2d_concept",
                requested_by="smoke-local",
            )
            prompt_plan = build_prompt_plan(
                brief_payload,
                provider_settings=PromptProviderSettings(
                    provider="local-deterministic",
                    model="local-concept-v1",
                    parameters={"external_calls": False, "quality": "concept", "size": "1x1"},
                    estimated_cost=Decimal("0.0000"),
                ),
            )

            await jobs.transition_job_status(
                session,
                job_result.job.id,
                status=JobStatus.RUNNING.value,
                message="Phase 3 smoke generation started.",
                source="smoke-local",
            )
            model_run = await jobs.create_model_run(
                session,
                job_result.job.id,
                estimated_cost=Decimal("0.0000"),
                input_artifact_ids=prompt_plan.input_artifact_ids,
                model=prompt_plan.model,
                parameters=prompt_plan.parameters,
                prompt_payload=prompt_plan.prompt_payload,
                prompt_text=prompt_plan.prompt_text,
                provider=prompt_plan.provider,
                status=ModelRunStatus.RUNNING.value,
            )
            await jobs.append_event(
                session,
                job_result.job.id,
                event_type=JobEventType.STATUS.value,
                status=JobStatus.RUNNING.value,
                message="Prompt planned.",
                source="smoke-local",
            )

            artifact_record_id = uuid4()
            object_key = build_object_key(
                filename="concept.png",
                kind=ArtifactKind.GENERATED_IMAGE.value,
                record_id=artifact_record_id,
                workspace_id=workspace.id,
            )
            await storage.put_object(object_key, PNG_1X1_BYTES, "image/png")
            version = await jobs.create_design_version(
                session,
                workspace.id,
                brief_id=brief.id,
                job_id=job_result.job.id,
                parameters={
                    "concept_label": prompt_plan.concept_label,
                    "external_calls": False,
                    "model": prompt_plan.model,
                    "provider": prompt_plan.provider,
                },
                status=DesignVersionStatus.GENERATED.value,
                summary="Generated 2D concept preview.",
                title="Generated concept preview",
            )
            artifact = await jobs.create_artifact(
                session,
                workspace.id,
                byte_size=len(PNG_1X1_BYTES),
                checksum_sha256=hashlib.sha256(PNG_1X1_BYTES).hexdigest(),
                content_type="image/png",
                height=1,
                job_id=job_result.job.id,
                kind=ArtifactKind.GENERATED_IMAGE.value,
                metadata={"external_calls": False, "smoke": "phase3"},
                object_key=object_key,
                version_id=version.id,
                width=1,
            )
            await jobs.complete_model_run(
                session,
                model_run.id,
                actual_cost=Decimal("0.0000"),
                output_artifact_id=artifact.id,
            )
            await jobs.update_job_costs(
                session,
                job_result.job.id,
                actual_cost=Decimal("0.0000"),
                estimated_cost=Decimal("0.0000"),
            )
            await jobs.transition_job_status(
                session,
                job_result.job.id,
                status=JobStatus.SUCCEEDED.value,
                message="Phase 3 smoke generation completed.",
                source="smoke-local",
            )

        async with session_scope(session_factory) as session:
            assert workspace_id is not None
            workspace_jobs = await jobs.list_workspace_jobs(session, workspace_id)
            artifacts = await jobs.list_workspace_artifacts(session, workspace_id)
            versions = await jobs.list_workspace_versions(session, workspace_id)
            events = await jobs.list_job_events(session, workspace_jobs[-1].id)
            model_runs = await jobs.list_job_model_runs(session, workspace_jobs[-1].id)

            if len(workspace_jobs) != 1 or workspace_jobs[0].status != JobStatus.SUCCEEDED.value:
                raise RuntimeError("Expected one succeeded Phase 3 smoke generation job")
            if len(artifacts) != 1 or artifacts[0].kind != ArtifactKind.GENERATED_IMAGE.value:
                raise RuntimeError("Expected one generated image artifact")
            if len(versions) != 1 or versions[0].status != DesignVersionStatus.GENERATED.value:
                raise RuntimeError("Expected one generated design version")
            if len(model_runs) != 1 or model_runs[0].status != ModelRunStatus.SUCCEEDED.value:
                raise RuntimeError("Expected one succeeded model run")
            if not model_runs[0].prompt_text or "concept preview" not in model_runs[0].prompt_text:
                raise RuntimeError("Expected model run prompt trace")
            if not any(event.event_type == JobEventType.COMPLETED.value for event in events):
                raise RuntimeError("Expected a completion event")
    finally:
        if workspace_id is not None:
            async with session_scope(session_factory) as session:
                workspace_to_delete = await session.get(Workspace, workspace_id)
                if workspace_to_delete is not None:
                    await session.delete(workspace_to_delete)
        await engine.dispose()
        shutil.rmtree(SMOKE_STORAGE_ROOT, ignore_errors=True)


def main() -> None:
    asyncio.run(run_smoke())
    print("Phase 3 local deterministic generation smoke passed.")


if __name__ == "__main__":
    main()
