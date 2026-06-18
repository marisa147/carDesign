from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from typing import TypedDict
from uuid import UUID, uuid4

from caragent_core.database import create_engine, create_session_factory, session_scope
from caragent_core.editing import EditIntent
from caragent_core.enums import (
    ArtifactKind,
    DesignVersionStatus,
    FailureCategory,
    JobEventType,
    JobStatus,
    ModelRunStatus,
)
from caragent_core.generation import (
    GenerationBriefPayload,
    PromptPlan,
    PromptProviderSettings,
    build_prompt_plan,
)
from caragent_core.models import (
    Artifact,
    DesignBrief,
    DesignVersion,
    GenerationJob,
    ModelRun,
    utc_now,
)
from caragent_core.provider_capabilities import (
    BFL_PROVIDER,
    LOCAL_PROVIDER,
    PROVIDER_MASKED_GENERATION_ROUTE,
)
from caragent_core.services import assets, jobs
from caragent_core.storage import FileObjectStorage, ObjectStorage, build_object_key
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_worker import __version__
from caragent_worker.app import celery_app
from caragent_worker.config import WorkerSettings, get_settings
from caragent_worker.providers import (
    ImageGenerationRequest,
    ImageGenerationResult,
    ImageProvider,
    ImageProviderConfigurationError,
    ImageProviderError,
    ImageProviderTimeoutError,
    MaskEditRequest,
    select_image_provider,
)
from caragent_worker.providers.base import sanitize_provider_error
from caragent_worker.recomposition import (
    RECOMPOSITION_MODEL,
    RECOMPOSITION_PROVIDER,
    RECOMPOSITION_ROUTE,
    DeterministicRecompositionError,
    recompose_targeted_edit,
)

LOCAL_SIMULATION_PROVIDER = "local-simulation"
LOCAL_SIMULATION_MODEL = "phase-2-no-provider"
LOCAL_SIMULATION_SOURCE = "worker-local-simulation"
JOB_CANCELED_MESSAGE = "Job canceled."
WORKER_CANCELED_MESSAGE = "Worker observed canceled job."
HOSTED_GUARD_REQUIRED_MESSAGE = (
    "Hosted calls require daily, per-minute, and per-job cost limits."
)
LOCAL_PROVIDER_NAMES = {"disabled", "local", "local-deterministic", RECOMPOSITION_PROVIDER}
BFL_PROVIDER_NAMES = {"bfl", "black-forest-labs"}


@dataclass(frozen=True, slots=True)
class JobProviderIntent:
    provider: str
    model: str
    parameters: dict[str, object]
    estimated_cost: Decimal | None = None


class LocalSimulationResult(TypedDict):
    external_calls: bool
    job_id: str
    model: str
    provider: str
    status: str


class Generate2DConceptResult(TypedDict, total=False):
    artifact_id: str
    error: str
    external_calls: bool
    job_id: str
    model: str
    model_run_id: str
    provider: str
    status: str
    version_id: str


@celery_app.task(name="caragent_worker.simulate_local_generation_job")  # type: ignore[untyped-decorator]
def simulate_local_generation_job(
    job_id: str,
    *,
    database_url: str | None = None,
    force_error_message: str | None = None,
) -> LocalSimulationResult:
    active_database_url = database_url or get_settings().database_url
    if active_database_url is None:
        raise RuntimeError("DATABASE_URL is required for local job simulation")

    return asyncio.run(
        _simulate_local_generation_job(
            active_database_url,
            UUID(job_id),
            force_error_message=force_error_message,
        ),
    )


@celery_app.task(name="caragent_worker.generate_2d_concept_job")  # type: ignore[untyped-decorator]
def generate_2d_concept_job(
    job_id: str,
    *,
    database_url: str | None = None,
) -> Generate2DConceptResult:
    settings = get_settings()
    active_database_url = database_url or settings.database_url
    if active_database_url is None:
        raise RuntimeError("DATABASE_URL is required for generation jobs")

    return asyncio.run(
        run_generate_2d_concept_job(
            active_database_url,
            UUID(job_id),
            settings=settings,
            storage=FileObjectStorage(root=Path(".caragent-generated")),
        ),
    )


async def run_generate_2d_concept_job(
    database_url: str,
    job_id: UUID,
    *,
    settings: WorkerSettings,
    storage: ObjectStorage,
    provider: ImageProvider | None = None,
) -> Generate2DConceptResult:
    engine = create_engine(database_url)
    session_factory = create_session_factory(engine)
    try:
        async with session_scope(session_factory) as session:
            return await _run_generate_2d_concept_job(
                session,
                job_id,
                provider=provider,
                settings=settings,
                storage=storage,
            )
    finally:
        await engine.dispose()


async def _run_generate_2d_concept_job(
    session: AsyncSession,
    job_id: UUID,
    *,
    settings: WorkerSettings,
    storage: ObjectStorage,
    provider: ImageProvider | None = None,
) -> Generate2DConceptResult:
    job: GenerationJob | None = None
    model_run_id: UUID | None = None
    failure_stage = "worker_start"
    failure_provider: str | None = None
    failure_model: str | None = None
    try:
        canceled_result = await _return_if_canceled(
            session,
            job_id,
            external_calls=False,
            stage="worker_start",
        )
        if canceled_result is not None:
            return canceled_result

        failure_stage = "job_transition_running"
        await jobs.transition_job_status(
            session,
            job_id,
            status=JobStatus.RUNNING.value,
            message="Generation worker started.",
            source="worker-generation",
        )
        job = await jobs.get_job(session, job_id)
        if job.brief_id is None:
            raise RuntimeError("Generation job requires a design brief")

        failure_stage = "brief_load"
        brief = await session.get(DesignBrief, job.brief_id)
        if brief is None:
            raise RuntimeError(f"Design brief not found: {job.brief_id}")

        failure_stage = "prompt_plan"
        parent_version_id, iteration_parameters = _generation_iteration_context(job.metadata_json)
        brief_payload = GenerationBriefPayload.model_validate(brief.payload)
        job_provider_intent = _job_provider_intent(job)
        if job_provider_intent is not None:
            failure_provider = job_provider_intent.provider
            failure_model = job_provider_intent.model
        prompt_plan = build_prompt_plan(
            brief_payload,
            provider_settings=_prompt_provider_settings(
                settings,
                job_provider_intent=job_provider_intent,
            ),
        )
        failure_provider = prompt_plan.provider
        failure_model = prompt_plan.model
        preview_spec = _preview_spec_from_prompt_payload(prompt_plan.prompt_payload)
        preview_spec_summary = _preview_spec_summary(preview_spec)
        input_artifact_ids = _input_artifact_ids(
            prompt_plan.input_artifact_ids,
            preview_spec=preview_spec,
        )
        await jobs.append_event(
            session,
            job_id,
            event_type=JobEventType.STATUS.value,
            status=JobStatus.RUNNING.value,
            message="Prompt planned.",
            source="worker-generation",
        )
        canceled_result = await _return_if_canceled(
            session,
            job_id,
            external_calls=False,
            stage="after_prompt_plan",
        )
        if canceled_result is not None:
            return canceled_result

        failure_stage = "targeted_edit_intent"
        edit_intent = _job_edit_intent(job)
        provider_mask_edit_intent: EditIntent | None = None
        if edit_intent is not None:
            if not settings.v2_targeted_regeneration_enabled:
                failure_stage = "targeted_regeneration_flag"
                raise ImageProviderConfigurationError(
                    "V2_TARGETED_REGENERATION_ENABLED is disabled.",
                )
            if edit_intent.route_preference == RECOMPOSITION_ROUTE:
                failure_stage = "recomposition_validation"
                failure_provider = RECOMPOSITION_PROVIDER
                failure_model = RECOMPOSITION_MODEL
                return await _run_deterministic_recomposition(
                    session,
                    job=job,
                    job_id=job_id,
                    parent_version_id=parent_version_id,
                    edit_intent=edit_intent,
                    iteration_parameters=iteration_parameters,
                    storage=storage,
                    settings=settings,
                )
            if edit_intent.route_preference == PROVIDER_MASKED_GENERATION_ROUTE:
                provider_mask_edit_intent = edit_intent

        provider_result: ImageGenerationResult | None = None
        request: ImageGenerationRequest | None = None
        model_run = None
        attempt_metadata: dict[str, object] = {}
        total_attempts = 0
        primary_attempts = settings.ai_generation_max_attempts

        for attempt_index in range(1, primary_attempts + 1):
            total_attempts += 1
            request = _image_request_from_prompt_plan(
                prompt_plan,
                edit_intent=provider_mask_edit_intent,
                input_artifact_ids=input_artifact_ids,
            )
            edit_route_metadata = _edit_route_metadata(request)
            model_run = await jobs.create_model_run(
                session,
                job_id,
                estimated_cost=prompt_plan.estimated_cost,
                input_artifact_ids=input_artifact_ids,
                model=request.model,
                parameters={
                    **prompt_plan.parameters,
                    **iteration_parameters,
                    **edit_route_metadata,
                    **preview_spec_summary,
                    "provider_attempt": attempt_index,
                    "provider_route": request.provider,
                },
                prompt_payload=request.prompt_payload,
                prompt_text=request.prompt_text,
                provider=request.provider,
                status=ModelRunStatus.RUNNING.value,
            )
            model_run_id = model_run.id
            try:
                failure_stage = "rights_check"
                await _require_confirmed_reference_rights(
                    session,
                    job.workspace_id,
                    input_artifact_ids,
                )
                canceled_result = await _return_if_canceled(
                    session,
                    job_id,
                    external_calls=False,
                    model_run_id=model_run_id,
                    stage="after_rights_check",
                )
                if canceled_result is not None:
                    return canceled_result

                failure_stage = "hosted_preflight"
                failure_provider = request.provider
                failure_model = request.model
                await _enforce_hosted_preflight(
                    session,
                    request,
                    settings=settings,
                    current_model_run_id=model_run_id,
                )
                if provider_mask_edit_intent is not None:
                    failure_stage = "provider_mask_preflight"
                    await _enforce_provider_mask_preflight(
                        session,
                        job=job,
                        parent_version_id=parent_version_id,
                        request=request,
                        settings=settings,
                    )
                active_provider = provider or select_image_provider(
                    settings,
                    provider_name=request.provider,
                )
                failure_stage = "provider_generate"
                failure_provider = request.provider
                failure_model = request.model
                provider_result = await active_provider.generate(request)
                canceled_result = await _return_if_canceled(
                    session,
                    job_id,
                    external_calls=True,
                    model_run_id=model_run_id,
                    stage="after_provider",
                )
                if canceled_result is not None:
                    return canceled_result
                attempt_metadata = {"provider_attempt_count": total_attempts}
                break
            except Exception as exc:
                sanitized_attempt_error = sanitize_provider_error(
                    str(exc),
                    secrets=_provider_secrets(settings),
                )
                attempt_category = _classify_generation_failure(exc, stage=failure_stage)
                await jobs.fail_model_run(
                    session,
                    model_run_id,
                    error_message=sanitized_attempt_error,
                )
                await jobs.append_event(
                    session,
                    job_id,
                    event_type=JobEventType.ERROR.value,
                    message="Provider attempt failed.",
                    metadata={
                        "error": sanitized_attempt_error,
                        "failure_category": attempt_category.value,
                        "model": failure_model,
                        "provider": failure_provider,
                        "provider_attempt": attempt_index,
                        "provider_attempt_count": total_attempts,
                        **_provider_failure_metadata(exc),
                        "stage": failure_stage,
                        "worker_version": __version__,
                    },
                    source="worker-generation",
                    status=JobStatus.RUNNING.value,
                )
                if _should_retry_provider_attempt(
                    attempt_category,
                    attempt_index,
                    primary_attempts,
                ):
                    continue
                if provider_mask_edit_intent is not None:
                    raise
                if not _should_fallback_to_local(
                    attempt_category,
                    primary_provider=request.provider,
                    settings=settings,
                ):
                    raise

                total_attempts += 1
                fallback_request = _image_request_from_prompt_plan(
                    prompt_plan,
                    edit_intent=provider_mask_edit_intent,
                    input_artifact_ids=input_artifact_ids,
                    provider_name=settings.ai_provider_fallback_name,
                )
                fallback_edit_route_metadata = _edit_route_metadata(fallback_request)
                fallback_metadata = {
                    "fallback_from_provider": request.provider,
                    "fallback_reason": sanitized_attempt_error,
                    "fallback_to_provider": fallback_request.provider,
                    "provider_attempt": total_attempts,
                    "provider_attempt_count": total_attempts,
                    "worker_version": __version__,
                }
                await jobs.append_event(
                    session,
                    job_id,
                    event_type=JobEventType.STATUS.value,
                    message="Fallback provider started.",
                    metadata=fallback_metadata,
                    source="worker-generation",
                    status=JobStatus.RUNNING.value,
                )
                model_run = await jobs.create_model_run(
                    session,
                    job_id,
                    estimated_cost=prompt_plan.estimated_cost,
                    input_artifact_ids=input_artifact_ids,
                    model=fallback_request.model,
                    parameters={
                        **prompt_plan.parameters,
                        **iteration_parameters,
                        **fallback_edit_route_metadata,
                        **preview_spec_summary,
                        **fallback_metadata,
                        "provider_attempt": total_attempts,
                        "provider_route": fallback_request.provider,
                    },
                    prompt_payload=fallback_request.prompt_payload,
                    prompt_text=fallback_request.prompt_text,
                    provider=fallback_request.provider,
                    status=ModelRunStatus.RUNNING.value,
                )
                model_run_id = model_run.id
                request = fallback_request
                try:
                    failure_stage = "hosted_preflight"
                    failure_provider = fallback_request.provider
                    failure_model = fallback_request.model
                    await _enforce_hosted_preflight(
                        session,
                        fallback_request,
                        settings=settings,
                        current_model_run_id=model_run_id,
                    )
                    if provider_mask_edit_intent is not None:
                        failure_stage = "provider_mask_preflight"
                        await _enforce_provider_mask_preflight(
                            session,
                            job=job,
                            parent_version_id=parent_version_id,
                            request=fallback_request,
                            settings=settings,
                        )
                    active_provider = select_image_provider(
                        settings,
                        provider_name=fallback_request.provider,
                    )
                    failure_stage = "provider_generate"
                    failure_provider = fallback_request.provider
                    failure_model = fallback_request.model
                    provider_result = await active_provider.generate(fallback_request)
                    canceled_result = await _return_if_canceled(
                        session,
                        job_id,
                        external_calls=bool(
                            provider_result.metadata.get("external_calls", True),
                        ),
                        model_run_id=model_run_id,
                        stage="after_provider",
                    )
                    if canceled_result is not None:
                        return canceled_result
                    attempt_metadata = {
                        "fallback_from_provider": prompt_plan.provider,
                        "fallback_reason": sanitized_attempt_error,
                        "fallback_to_provider": fallback_request.provider,
                        "provider_attempt_count": total_attempts,
                    }
                    break
                except Exception as fallback_exc:
                    sanitized_fallback_error = sanitize_provider_error(
                        str(fallback_exc),
                        secrets=_provider_secrets(settings),
                    )
                    await jobs.fail_model_run(
                        session,
                        model_run_id,
                        error_message=sanitized_fallback_error,
                    )
                    raise

        if provider_result is None or request is None or model_run is None:
            raise RuntimeError("Generation provider did not produce a result")

        provider_trace_metadata = _provider_trace_metadata(request, provider_result)
        artifact_metadata = {
            **provider_result.metadata,
            **provider_trace_metadata,
            **preview_spec_summary,
            **attempt_metadata,
            "concept_label": request.concept_label,
            "preview_spec": preview_spec,
        }
        object_key = build_object_key(
            filename="concept.png",
            kind=ArtifactKind.GENERATED_IMAGE.value,
            record_id=uuid4(),
            workspace_id=job.workspace_id,
        )
        failure_stage = "storage_put"
        await storage.put_object(
            object_key,
            provider_result.image_bytes,
            provider_result.content_type,
        )

        failure_stage = "version_write"
        version = await jobs.create_design_version(
            session,
            job.workspace_id,
            brief_id=job.brief_id,
            job_id=job_id,
            parent_version_id=parent_version_id,
            parameters={
                "concept_label": request.concept_label,
                **iteration_parameters,
                **attempt_metadata,
                "model": provider_result.model,
                **provider_trace_metadata,
                "preview_spec": preview_spec,
                "provider": provider_result.provider,
                **preview_spec_summary,
            },
            status=DesignVersionStatus.GENERATED.value,
            summary="Generated 2D concept preview.",
            title="Generated concept preview",
        )
        artifact = await jobs.create_artifact(
            session,
            job.workspace_id,
            byte_size=len(provider_result.image_bytes),
            checksum_sha256=hashlib.sha256(provider_result.image_bytes).hexdigest(),
            content_type=provider_result.content_type,
            height=provider_result.height,
            job_id=job_id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            metadata=artifact_metadata,
            object_key=object_key,
            version_id=version.id,
            width=provider_result.width,
        )
        await jobs.append_event(
            session,
            job_id,
            event_type=JobEventType.STATUS.value,
            status=JobStatus.RUNNING.value,
            message="Generated artifact stored.",
            source="worker-generation",
        )
        await jobs.append_event(
            session,
            job_id,
            event_type=JobEventType.STATUS.value,
            status=JobStatus.RUNNING.value,
            message="Design version created.",
            source="worker-generation",
        )
        await jobs.complete_model_run(
            session,
            model_run.id,
            actual_cost=provider_result.actual_cost,
            output_artifact_id=artifact.id,
        )
        await jobs.update_job_costs(
            session,
            job_id,
            actual_cost=provider_result.actual_cost,
            estimated_cost=provider_result.estimated_cost,
        )
        canceled_result = await _return_if_canceled(
            session,
            job_id,
            external_calls=True,
            model_run_id=model_run_id,
            stage="before_success",
        )
        if canceled_result is not None:
            return canceled_result
        await jobs.transition_job_status(
            session,
            job_id,
            status=JobStatus.SUCCEEDED.value,
            message="Generation completed.",
            metadata={
                **attempt_metadata,
                **provider_trace_metadata,
                "external_calls": bool(provider_result.metadata.get("external_calls", True)),
                "model": provider_result.model,
                "provider": provider_result.provider,
                "stage": "completed",
                "worker_version": __version__,
            },
            source="worker-generation",
        )

        return {
            "artifact_id": str(artifact.id),
            "external_calls": bool(provider_result.metadata.get("external_calls", True)),
            "job_id": str(job_id),
            "model": provider_result.model,
            "model_run_id": str(model_run.id),
            "provider": provider_result.provider,
            "status": JobStatus.SUCCEEDED.value,
            "version_id": str(version.id),
        }
    except Exception as exc:
        sanitized_error = sanitize_provider_error(str(exc), secrets=_provider_secrets(settings))
        failure_category = _classify_generation_failure(exc, stage=failure_stage)
        failure_metadata: dict[str, object] = {
            "error": sanitized_error,
            "failure_category": failure_category.value,
            "model": failure_model,
            "provider": failure_provider,
            **_provider_failure_metadata(exc),
            "stage": failure_stage,
            "worker_version": __version__,
        }
        if job is not None:
            failure_metadata.update(
                _targeted_edit_failure_metadata(
                    job,
                    failure_category=failure_category,
                    sanitized_error=sanitized_error,
                ),
            )
        if model_run_id is not None:
            await jobs.fail_model_run(
                session,
                model_run_id,
                error_message=sanitized_error,
            )
        await jobs.transition_job_status(
            session,
            job_id,
            status=JobStatus.FAILED.value,
            latest_error=sanitized_error,
            metadata=failure_metadata,
            message="Generation failed.",
            source="worker-generation",
        )
        return {
            "error": sanitized_error,
            "external_calls": False,
            "job_id": str(job_id),
            "status": JobStatus.FAILED.value,
        }


async def _run_deterministic_recomposition(
    session: AsyncSession,
    *,
    edit_intent: EditIntent,
    iteration_parameters: dict[str, object],
    job: GenerationJob,
    job_id: UUID,
    parent_version_id: UUID | None,
    settings: WorkerSettings,
    storage: ObjectStorage,
) -> Generate2DConceptResult:
    model_run_id: UUID | None = None
    try:
        parent_version, parent_artifact, parent_preview_spec = (
            await _load_recomposition_parent_context(
                session,
                edit_intent=edit_intent,
                parent_version_id=parent_version_id,
                workspace_id=job.workspace_id,
            )
        )
        recomposition = recompose_targeted_edit(
            parent_preview_spec,
            edit_intent,
            height=settings.ai_local_image_height,
            width=settings.ai_local_image_width,
        )
        preview_spec_summary = _preview_spec_summary(recomposition.preview_spec)
        targeted_edit_metadata = _edit_intent_metadata(edit_intent)
        trace_metadata: dict[str, object] = {
            **preview_spec_summary,
            **targeted_edit_metadata,
            "changed_fields": list(recomposition.metadata["changed_fields"]),
            "external_calls": False,
            "parent_artifact_id": str(parent_artifact.id),
            "parent_version_id": str(parent_version.id),
            "provider_route": RECOMPOSITION_ROUTE,
            "recomposition_route": RECOMPOSITION_ROUTE,
            "target": recomposition.metadata["target"],
            "worker_version": __version__,
        }
        model_run = await jobs.create_model_run(
            session,
            job_id,
            actual_cost=Decimal("0.0000"),
            estimated_cost=Decimal("0.0000"),
            input_artifact_ids=[str(parent_artifact.id)],
            model=RECOMPOSITION_MODEL,
            parameters={
                **iteration_parameters,
                **trace_metadata,
            },
            prompt_payload={
                "edit_intent": edit_intent.model_dump(mode="json"),
                "mask_edit": targeted_edit_metadata,
                "parent_preview_spec": parent_preview_spec,
                "preview_spec": recomposition.preview_spec,
            },
            prompt_text=edit_intent.prompt_delta.summary,
            provider=RECOMPOSITION_PROVIDER,
            status=ModelRunStatus.RUNNING.value,
        )
        model_run_id = model_run.id
        await jobs.append_event(
            session,
            job_id,
            event_type=JobEventType.STATUS.value,
            message="Deterministic recomposition started.",
            metadata=trace_metadata,
            source="worker-generation",
            status=JobStatus.RUNNING.value,
        )
        canceled_result = await _return_if_canceled(
            session,
            job_id,
            external_calls=False,
            model_run_id=model_run_id,
            stage="before_recomposition",
        )
        if canceled_result is not None:
            return canceled_result

        object_key = build_object_key(
            filename="concept.png",
            kind=ArtifactKind.GENERATED_IMAGE.value,
            record_id=uuid4(),
            workspace_id=job.workspace_id,
        )
        await storage.put_object(
            object_key,
            recomposition.image_bytes,
            recomposition.content_type,
        )
        version = await jobs.create_design_version(
            session,
            job.workspace_id,
            brief_id=job.brief_id,
            job_id=job_id,
            parent_version_id=parent_version.id,
            parameters={
                "concept_label": "targeted_recomposition",
                **iteration_parameters,
                **trace_metadata,
                "model": RECOMPOSITION_MODEL,
                "preview_spec": recomposition.preview_spec,
                "provider": RECOMPOSITION_PROVIDER,
            },
            status=DesignVersionStatus.GENERATED.value,
            summary="Recomposed targeted 2D concept preview.",
            title="Targeted recomposition preview",
        )
        artifact = await jobs.create_artifact(
            session,
            job.workspace_id,
            byte_size=len(recomposition.image_bytes),
            checksum_sha256=hashlib.sha256(recomposition.image_bytes).hexdigest(),
            content_type=recomposition.content_type,
            height=recomposition.height,
            job_id=job_id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            metadata={
                **recomposition.metadata,
                **iteration_parameters,
                **trace_metadata,
            },
            object_key=object_key,
            version_id=version.id,
            width=recomposition.width,
        )
        await jobs.append_event(
            session,
            job_id,
            event_type=JobEventType.STATUS.value,
            status=JobStatus.RUNNING.value,
            message="Generated artifact stored.",
            source="worker-generation",
        )
        await jobs.append_event(
            session,
            job_id,
            event_type=JobEventType.STATUS.value,
            status=JobStatus.RUNNING.value,
            message="Design version created.",
            source="worker-generation",
        )
        await jobs.complete_model_run(
            session,
            model_run.id,
            actual_cost=Decimal("0.0000"),
            output_artifact_id=artifact.id,
        )
        await jobs.update_job_costs(
            session,
            job_id,
            actual_cost=Decimal("0.0000"),
            estimated_cost=Decimal("0.0000"),
        )
        canceled_result = await _return_if_canceled(
            session,
            job_id,
            external_calls=False,
            model_run_id=model_run_id,
            stage="before_success",
        )
        if canceled_result is not None:
            return canceled_result
        await jobs.transition_job_status(
            session,
            job_id,
            status=JobStatus.SUCCEEDED.value,
            message="Generation completed.",
            metadata={
                **trace_metadata,
                "model": RECOMPOSITION_MODEL,
                "provider": RECOMPOSITION_PROVIDER,
                "stage": "completed",
            },
            source="worker-generation",
        )
        return {
            "artifact_id": str(artifact.id),
            "external_calls": False,
            "job_id": str(job_id),
            "model": RECOMPOSITION_MODEL,
            "model_run_id": str(model_run.id),
            "provider": RECOMPOSITION_PROVIDER,
            "status": JobStatus.SUCCEEDED.value,
            "version_id": str(version.id),
        }
    except Exception:
        if model_run_id is not None:
            await jobs.fail_model_run(
                session,
                model_run_id,
                error_message="Deterministic recomposition failed.",
            )
        raise


async def _simulate_local_generation_job(
    database_url: str,
    job_id: UUID,
    *,
    force_error_message: str | None = None,
) -> LocalSimulationResult:
    engine = create_engine(database_url)
    session_factory = create_session_factory(engine)
    try:
        async with session_scope(session_factory) as session:
            await jobs.transition_job_status(
                session,
                job_id,
                status=JobStatus.RUNNING.value,
                message="Local no-provider simulation started.",
                source=LOCAL_SIMULATION_SOURCE,
            )

            if force_error_message is not None:
                await jobs.create_model_run(
                    session,
                    job_id,
                    actual_cost=Decimal("0.0000"),
                    estimated_cost=Decimal("0.0000"),
                    model=LOCAL_SIMULATION_MODEL,
                    parameters={"external_calls": False},
                    provider=LOCAL_SIMULATION_PROVIDER,
                    status=ModelRunStatus.FAILED.value,
                )
                await jobs.transition_job_status(
                    session,
                    job_id,
                    status=JobStatus.FAILED.value,
                    message="Local no-provider simulation failed.",
                    source=LOCAL_SIMULATION_SOURCE,
                    latest_error=force_error_message,
                )
                return _result(job_id, JobStatus.FAILED.value)

            await jobs.create_model_run(
                session,
                job_id,
                actual_cost=Decimal("0.0000"),
                estimated_cost=Decimal("0.0000"),
                model=LOCAL_SIMULATION_MODEL,
                parameters={"external_calls": False},
                provider=LOCAL_SIMULATION_PROVIDER,
                status=ModelRunStatus.SUCCEEDED.value,
            )
            await jobs.update_job_costs(
                session,
                job_id,
                actual_cost=Decimal("0.0000"),
                estimated_cost=Decimal("0.0000"),
            )
            await jobs.transition_job_status(
                session,
                job_id,
                status=JobStatus.SUCCEEDED.value,
                message="Local no-provider simulation completed.",
                source=LOCAL_SIMULATION_SOURCE,
            )
            return _result(job_id, JobStatus.SUCCEEDED.value)
    finally:
        await engine.dispose()


def _result(job_id: UUID, status: str) -> LocalSimulationResult:
    return {
        "external_calls": False,
        "job_id": str(job_id),
        "model": LOCAL_SIMULATION_MODEL,
        "provider": LOCAL_SIMULATION_PROVIDER,
        "status": status,
    }


def _classify_generation_failure(exc: Exception, *, stage: str) -> FailureCategory:
    if isinstance(exc, ImageProviderTimeoutError):
        return FailureCategory.TIMEOUT
    if isinstance(exc, DeterministicRecompositionError):
        message = str(exc).lower()
        if "target" in message or "parent" in message or "previewspec" in message:
            return FailureCategory.TARGETED_EDIT_INVALID
        return FailureCategory.TARGETED_EDIT_CONFLICT
    if isinstance(exc, ImageProviderConfigurationError):
        if stage in {"provider_mask_preflight", "targeted_edit_intent"}:
            message = str(exc).lower()
            if "does not support" in message or "disabled" in message:
                return FailureCategory.TARGETED_EDIT_UNSUPPORTED
            return FailureCategory.TARGETED_EDIT_INVALID
        if stage == "targeted_regeneration_flag":
            return FailureCategory.TARGETED_EDIT_UNSUPPORTED
        return FailureCategory.PROVIDER_CONFIGURATION
    if isinstance(exc, ImageProviderError):
        return FailureCategory.PROVIDER
    if isinstance(exc, PermissionError):
        return FailureCategory.VALIDATION_RIGHTS
    if stage == "storage_put" or isinstance(exc, OSError):
        return FailureCategory.STORAGE
    return FailureCategory.UNKNOWN


def _targeted_edit_failure_metadata(
    job: GenerationJob,
    *,
    failure_category: FailureCategory,
    sanitized_error: str,
) -> dict[str, object]:
    try:
        edit_intent = _job_edit_intent(job)
    except ImageProviderConfigurationError:
        return {
            "blocked_reason": sanitized_error,
            "retry_eligible": False,
            "retry_route": None,
        }
    if edit_intent is None:
        return {}

    retry_eligible = _is_targeted_edit_retry_eligible(failure_category)
    metadata: dict[str, object] = {
        **_edit_intent_metadata(edit_intent),
        "blocked_reason": None if retry_eligible else sanitized_error,
        "edit_intent": edit_intent.model_dump(mode="json"),
        "retry_eligible": retry_eligible,
        "retry_route": edit_intent.route_preference,
    }
    return metadata


def _is_targeted_edit_retry_eligible(failure_category: FailureCategory) -> bool:
    return failure_category in {
        FailureCategory.PROVIDER,
        FailureCategory.STORAGE,
        FailureCategory.TIMEOUT,
    }


def _provider_failure_metadata(exc: Exception) -> dict[str, object]:
    metadata: dict[str, object] = {}
    if isinstance(exc, ImageProviderError):
        if exc.provider_status:
            metadata["provider_status"] = exc.provider_status
        if exc.status_code is not None:
            metadata["provider_status_code"] = exc.status_code
    failure_kind = _provider_failure_kind(exc)
    if failure_kind is not None:
        metadata["provider_failure_kind"] = failure_kind
    return metadata


def _provider_failure_kind(exc: Exception) -> str | None:
    if isinstance(exc, ImageProviderTimeoutError):
        return "timeout"
    if isinstance(exc, ImageProviderConfigurationError):
        return "provider_configuration"
    if not isinstance(exc, ImageProviderError):
        return None

    status = (exc.provider_status or "").strip().lower()
    if status in {"request_moderated", "content_moderated"}:
        return "moderation"
    if status == "provider_validation":
        return "provider_validation"
    if status == "insufficient_credits":
        return "insufficient_credits"
    if status == "rate_limited":
        return "rate_limit"
    if status in {"task_not_found"}:
        return "provider_not_found"
    if status:
        return "provider_error"
    return "provider_error"


def _should_retry_provider_attempt(
    category: FailureCategory,
    attempt_index: int,
    max_attempts: int,
) -> bool:
    return category in {
        FailureCategory.PROVIDER,
        FailureCategory.TIMEOUT,
    } and attempt_index < max_attempts


def _should_fallback_to_local(
    category: FailureCategory,
    *,
    primary_provider: str,
    settings: WorkerSettings,
) -> bool:
    if category not in {FailureCategory.PROVIDER, FailureCategory.TIMEOUT}:
        return False
    if not settings.ai_provider_fallback_enabled:
        return False
    return primary_provider.strip().lower() not in {
        "disabled",
        "local",
        "local-deterministic",
    }


async def _enforce_hosted_preflight(
    session: AsyncSession,
    request: ImageGenerationRequest,
    *,
    current_model_run_id: UUID,
    settings: WorkerSettings,
) -> None:
    if _is_local_provider(request.provider):
        return
    if not settings.v2_hosted_provider_rollout_enabled:
        raise ImageProviderConfigurationError("V2_HOSTED_PROVIDER_ROLLOUT_ENABLED is disabled.")
    if not settings.ai_provider_calls_enabled:
        raise ImageProviderConfigurationError("AI_PROVIDER_CALLS_ENABLED is disabled.")
    if _is_bfl_provider(request.provider) and not (
        settings.ai_provider_bfl_api_key
        and settings.ai_provider_bfl_api_key.get_secret_value()
    ):
        raise ImageProviderConfigurationError("AI_PROVIDER_BFL_API_KEY is missing.")
    if (
        settings.ai_hosted_daily_call_limit is None
        or settings.ai_hosted_rate_limit_per_minute is None
        or settings.ai_max_estimated_cost_per_job is None
    ):
        raise ImageProviderConfigurationError(HOSTED_GUARD_REQUIRED_MESSAGE)
    if (
        request.estimated_cost is not None
        and request.estimated_cost > settings.ai_max_estimated_cost_per_job
    ):
        raise ImageProviderConfigurationError(
            "Hosted provider estimated cost exceeds per-job limit.",
        )

    now = utc_now()
    daily_count = await _count_recent_hosted_model_runs(
        session,
        current_model_run_id=current_model_run_id,
        since=now - timedelta(days=1),
    )
    if daily_count >= settings.ai_hosted_daily_call_limit:
        raise ImageProviderConfigurationError("Hosted provider daily call limit reached.")

    minute_count = await _count_recent_hosted_model_runs(
        session,
        current_model_run_id=current_model_run_id,
        since=now - timedelta(minutes=1),
    )
    if minute_count >= settings.ai_hosted_rate_limit_per_minute:
        raise ImageProviderConfigurationError("Hosted provider per-minute rate limit reached.")


async def _enforce_provider_mask_preflight(
    session: AsyncSession,
    *,
    job: GenerationJob,
    parent_version_id: UUID | None,
    request: ImageGenerationRequest,
    settings: WorkerSettings,
) -> None:
    mask_edit = request.mask_edit
    if mask_edit is None:
        raise ImageProviderConfigurationError(
            "provider_masked_generation requires mask edit metadata.",
        )
    if parent_version_id is None:
        raise ImageProviderConfigurationError(
            "provider_masked_generation requires a parent version.",
        )
    if (
        mask_edit.parent_version_id is not None
        and mask_edit.parent_version_id != str(parent_version_id)
    ):
        raise ImageProviderConfigurationError(
            "provider_masked_generation parent version does not match job.",
        )

    _require_provider_mask_capability(request.provider, settings=settings)

    mask_artifact_id = UUID(mask_edit.mask_artifact_id)
    mask_artifact = await session.get(Artifact, mask_artifact_id)
    if mask_artifact is None or mask_artifact.workspace_id != job.workspace_id:
        raise ImageProviderConfigurationError(
            "provider_masked_generation mask artifact was not found.",
        )
    if mask_artifact.content_type != mask_edit.mask_content_type:
        raise ImageProviderConfigurationError(
            "provider_masked_generation mask content type does not match artifact.",
        )
    if mask_artifact.width != mask_edit.mask_width or mask_artifact.height != mask_edit.mask_height:
        raise ImageProviderConfigurationError(
            "provider_masked_generation mask dimensions do not match artifact.",
        )


def _require_provider_mask_capability(
    provider_name: str,
    *,
    settings: WorkerSettings,
) -> None:
    provider_key = _capability_provider_key(provider_name)
    capability = settings.provider_capability_map().get(provider_key)
    if capability is None:
        raise ImageProviderConfigurationError(
            f"Provider {provider_name} does not support {PROVIDER_MASKED_GENERATION_ROUTE}.",
        )
    supported_routes = {str(route) for route in capability.get("supported_edit_routes", [])}
    raw_supports = capability.get("supports")
    supports = raw_supports if isinstance(raw_supports, dict) else {}
    raw_mask_input = capability.get("mask_input")
    mask_input = raw_mask_input if isinstance(raw_mask_input, dict) else {}
    if (
        PROVIDER_MASKED_GENERATION_ROUTE not in supported_routes
        or not bool(supports.get("mask_aware_generation"))
        or not bool(mask_input.get("accepted"))
    ):
        blocked_reason = str(
            mask_input.get("blocked_reason")
            or f"Route {PROVIDER_MASKED_GENERATION_ROUTE} is not enabled.",
        )
        raise ImageProviderConfigurationError(
            f"Provider {provider_key} does not support "
            f"{PROVIDER_MASKED_GENERATION_ROUTE}: {blocked_reason}",
        )


def _capability_provider_key(provider_name: str) -> str:
    normalized = provider_name.strip().lower()
    if normalized in LOCAL_PROVIDER_NAMES:
        return LOCAL_PROVIDER
    if normalized in BFL_PROVIDER_NAMES:
        return BFL_PROVIDER
    return normalized


async def _count_recent_hosted_model_runs(
    session: AsyncSession,
    *,
    current_model_run_id: UUID,
    since: object,
) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(ModelRun)
        .where(
            ModelRun.created_at >= since,
            ModelRun.id != current_model_run_id,
            ModelRun.provider.is_not(None),
            ~ModelRun.provider.in_(LOCAL_PROVIDER_NAMES),
        ),
    )
    return int(result.scalar_one())


def _is_local_provider(provider_name: str) -> bool:
    return provider_name.strip().lower() in LOCAL_PROVIDER_NAMES


def _is_bfl_provider(provider_name: str) -> bool:
    return provider_name.strip().lower() in BFL_PROVIDER_NAMES


async def _return_if_canceled(
    session: AsyncSession,
    job_id: UUID,
    *,
    external_calls: bool,
    stage: str,
    model_run_id: UUID | None = None,
) -> Generate2DConceptResult | None:
    job = await jobs.get_job(session, job_id)
    await session.refresh(job)
    if job.status != JobStatus.CANCELED.value:
        return None

    if model_run_id is not None:
        model_run = await jobs.get_model_run(session, model_run_id)
        await session.refresh(model_run)
        if model_run.status in {
            ModelRunStatus.PLANNED.value,
            ModelRunStatus.RUNNING.value,
        }:
            await jobs.fail_model_run(
                session,
                model_run_id,
                error_message=JOB_CANCELED_MESSAGE,
            )

    await jobs.append_event(
        session,
        job_id,
        event_type=JobEventType.STATUS.value,
        message=WORKER_CANCELED_MESSAGE,
        metadata={
            "failure_category": FailureCategory.CANCELED.value,
            "stage": stage,
            "worker_version": __version__,
        },
        source="worker-generation",
        status=JobStatus.CANCELED.value,
    )
    return {
        "external_calls": external_calls,
        "job_id": str(job_id),
        "status": JobStatus.CANCELED.value,
    }


def _prompt_provider_settings(
    settings: WorkerSettings,
    *,
    job_provider_intent: JobProviderIntent | None = None,
) -> PromptProviderSettings:
    if job_provider_intent is not None:
        if (
            job_provider_intent.provider not in LOCAL_PROVIDER_NAMES
            and job_provider_intent.provider not in BFL_PROVIDER_NAMES
        ):
            raise ImageProviderConfigurationError(
                f"Unsupported image provider: {job_provider_intent.provider}",
            )
        return PromptProviderSettings(
            estimated_cost=job_provider_intent.estimated_cost,
            model=job_provider_intent.model,
            parameters=job_provider_intent.parameters,
            provider=job_provider_intent.provider,
        )

    provider = (
        settings.ai_provider_default
        if settings.ai_provider_calls_enabled and settings.ai_provider_default != "disabled"
        else "local-deterministic"
    )
    model = settings.ai_provider_model
    return PromptProviderSettings(
        model=model,
        parameters={
            "quality": "concept",
            "size": f"{settings.ai_local_image_width}x{settings.ai_local_image_height}",
        },
        provider=provider,
    )


def _job_provider_intent(job: GenerationJob) -> JobProviderIntent | None:
    metadata = job.metadata_json if isinstance(job.metadata_json, dict) else {}
    raw_intent = metadata.get("provider_intent")
    intent = raw_intent if isinstance(raw_intent, dict) else {}
    provider = _optional_text(intent.get("provider")) or _optional_text(job.provider)
    model = _optional_text(intent.get("model")) or _optional_text(job.model)
    parameters = intent.get("parameters")

    if provider is None and model is None and not isinstance(parameters, dict):
        return None
    if provider is None:
        raise ImageProviderConfigurationError("Provider intent is missing provider.")
    if model is None:
        raise ImageProviderConfigurationError("Provider intent is missing model.")

    normalized_provider = provider.strip().lower()
    if normalized_provider == "local":
        normalized_provider = "local-deterministic"

    return JobProviderIntent(
        estimated_cost=job.estimated_cost,
        model=model.strip(),
        parameters={
            str(key): value
            for key, value in (parameters if isinstance(parameters, dict) else {}).items()
        },
        provider=normalized_provider,
    )


def _job_edit_intent(job: GenerationJob) -> EditIntent | None:
    metadata = job.metadata_json if isinstance(job.metadata_json, dict) else {}
    raw_intent = metadata.get("edit_intent")
    if raw_intent is None:
        return None
    if not isinstance(raw_intent, dict):
        raise ImageProviderConfigurationError("Invalid targeted edit intent metadata.")
    try:
        return EditIntent.model_validate(raw_intent)
    except ValidationError as exc:
        raise ImageProviderConfigurationError(
            "Invalid targeted edit intent metadata.",
        ) from exc


async def _load_recomposition_parent_context(
    session: AsyncSession,
    *,
    edit_intent: EditIntent,
    parent_version_id: UUID | None,
    workspace_id: UUID,
) -> tuple[DesignVersion, Artifact, dict[str, object]]:
    if parent_version_id is None:
        raise DeterministicRecompositionError("targeted recomposition requires parent version")
    if (
        edit_intent.parent_version_id is not None
        and edit_intent.parent_version_id != parent_version_id
    ):
        raise DeterministicRecompositionError("edit intent parent version does not match job")

    parent_version = await session.get(DesignVersion, parent_version_id)
    if parent_version is None or parent_version.workspace_id != workspace_id:
        raise DeterministicRecompositionError(f"parent version not found: {parent_version_id}")

    result = await session.execute(
        select(Artifact)
        .where(
            Artifact.kind == ArtifactKind.GENERATED_IMAGE.value,
            Artifact.version_id == parent_version_id,
            Artifact.workspace_id == workspace_id,
        )
        .order_by(Artifact.created_at.desc()),
    )
    parent_artifact = result.scalars().first()
    if parent_artifact is None:
        raise DeterministicRecompositionError(
            f"parent generated artifact not found: {parent_version_id}",
        )

    preview_spec = _parent_preview_spec(parent_version, parent_artifact)
    if not preview_spec:
        raise DeterministicRecompositionError("parent PreviewSpec not found")
    return parent_version, parent_artifact, preview_spec


def _parent_preview_spec(
    parent_version: DesignVersion,
    parent_artifact: Artifact,
) -> dict[str, object]:
    version_parameters = (
        parent_version.parameters if isinstance(parent_version.parameters, dict) else {}
    )
    artifact_metadata = (
        parent_artifact.metadata_json if isinstance(parent_artifact.metadata_json, dict) else {}
    )
    for source in (version_parameters, artifact_metadata):
        preview_spec = source.get("preview_spec")
        if isinstance(preview_spec, dict):
            return dict(preview_spec)
    return {}


def _optional_text(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _generation_iteration_context(metadata: object) -> tuple[UUID | None, dict[str, object]]:
    if not isinstance(metadata, dict):
        return None, {}

    parent_version_id_value = metadata.get("parent_version_id")
    if not parent_version_id_value:
        return None, {}

    parent_version_id = UUID(str(parent_version_id_value))
    iteration_parameters: dict[str, object] = {
        "iteration": True,
        "parent_version_id": str(parent_version_id),
    }
    change_request = metadata.get("change_request")
    if isinstance(change_request, str) and change_request.strip():
        iteration_parameters["change_request"] = change_request

    parameter_overrides = metadata.get("parameter_overrides")
    if isinstance(parameter_overrides, dict):
        iteration_parameters["parameter_overrides"] = {
            str(key): value for key, value in parameter_overrides.items()
        }

    return parent_version_id, iteration_parameters


def _image_request_from_prompt_plan(
    prompt_plan: PromptPlan,
    *,
    edit_intent: EditIntent | None = None,
    input_artifact_ids: list[str],
    provider_name: str | None = None,
) -> ImageGenerationRequest:
    request = ImageGenerationRequest.from_prompt_plan(prompt_plan)
    mask_edit = _mask_edit_request_from_intent(edit_intent)
    prompt_payload = dict(request.prompt_payload)
    if mask_edit is not None:
        prompt_payload["mask_edit"] = _mask_edit_metadata(mask_edit)
    return ImageGenerationRequest(
        concept_label=request.concept_label,
        estimated_cost=request.estimated_cost,
        input_artifact_ids=input_artifact_ids,
        mask_edit=mask_edit,
        model=request.model,
        parameters=request.parameters,
        prompt_payload=prompt_payload,
        prompt_text=request.prompt_text,
        provider=provider_name or request.provider,
    )


def _mask_edit_request_from_intent(edit_intent: EditIntent | None) -> MaskEditRequest | None:
    if edit_intent is None:
        return None
    return MaskEditRequest(
        mask_artifact_id=str(edit_intent.mask.artifact_id),
        mask_content_type=edit_intent.mask.content_type,
        mask_height=edit_intent.mask.height,
        mask_width=edit_intent.mask.width,
        parent_version_id=(
            str(edit_intent.parent_version_id)
            if edit_intent.parent_version_id is not None
            else None
        ),
        prompt_delta=edit_intent.prompt_delta.model_dump(mode="json"),
        region=edit_intent.region.model_dump(mode="json"),
        route_preference=edit_intent.route_preference,
        target=edit_intent.target.model_dump(mode="json"),
    )


def _edit_intent_metadata(edit_intent: EditIntent) -> dict[str, object]:
    mask_edit = _mask_edit_request_from_intent(edit_intent)
    if mask_edit is None:
        return {}
    return _mask_edit_metadata(mask_edit)


def _provider_trace_metadata(
    request: ImageGenerationRequest,
    result: ImageGenerationResult,
) -> dict[str, object]:
    metadata: dict[str, object] = {
        "actual_cost": _decimal_metadata(result.actual_cost),
        "estimated_cost": _decimal_metadata(result.estimated_cost),
        "model": result.model,
        "provider": result.provider,
        "provider_parameters": dict(request.parameters),
    }
    metadata.update(_edit_route_metadata(request))
    return metadata


def _edit_route_metadata(request: ImageGenerationRequest) -> dict[str, object]:
    if request.mask_edit is None:
        return {}
    return _mask_edit_metadata(request.mask_edit)


def _mask_edit_metadata(mask_edit: MaskEditRequest) -> dict[str, object]:
    return {
        "edit_route": mask_edit.route_preference,
        "mask_artifact_id": mask_edit.mask_artifact_id,
        "mask_content_type": mask_edit.mask_content_type,
        "mask_height": mask_edit.mask_height,
        "mask_width": mask_edit.mask_width,
        "parent_version_id": mask_edit.parent_version_id,
        "prompt_delta": dict(mask_edit.prompt_delta),
        "region": dict(mask_edit.region),
        "target": dict(mask_edit.target),
    }


def _decimal_metadata(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return f"{value:.4f}"


def _preview_spec_from_prompt_payload(prompt_payload: dict[str, object]) -> dict[str, object]:
    preview_spec = prompt_payload.get("preview_spec")
    return dict(preview_spec) if isinstance(preview_spec, dict) else {}


def _preview_spec_summary(preview_spec: dict[str, object]) -> dict[str, object]:
    return {
        "overlay_layer_count": len(_json_list(preview_spec.get("overlay_layers"))),
        "safe_zone_count": len(_json_list(preview_spec.get("safe_zones"))),
        "warning_count": len(_json_list(preview_spec.get("warnings"))),
    }


def _input_artifact_ids(
    reference_asset_ids: list[str],
    *,
    preview_spec: dict[str, object],
) -> list[str]:
    artifact_ids = list(reference_asset_ids)
    sources = preview_spec.get("sources")
    if isinstance(sources, dict):
        for value in _json_list(sources.get("overlay_logo_asset_ids")):
            asset_id = str(value)
            if asset_id and asset_id not in artifact_ids:
                artifact_ids.append(asset_id)
    return artifact_ids


def _json_list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


async def _require_confirmed_reference_rights(
    session: AsyncSession,
    workspace_id: UUID,
    reference_asset_ids: list[str],
) -> None:
    for asset_id_text in reference_asset_ids:
        asset = await assets.require_confirmed_rights(session, UUID(asset_id_text))
        if asset.workspace_id != workspace_id:
            raise PermissionError(f"Asset does not belong to workspace: {asset.id}")


def _provider_secrets(settings: WorkerSettings) -> list[str]:
    secrets = [
        settings.ai_provider_openai_api_key,
        settings.ai_provider_fal_api_key,
        settings.ai_provider_bfl_api_key,
    ]
    return [secret.get_secret_value() for secret in secrets if secret is not None]
