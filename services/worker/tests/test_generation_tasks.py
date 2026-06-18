from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from caragent_core.database import create_engine, create_session_factory, session_scope
from caragent_core.enums import (
    ArtifactKind,
    AssetKind,
    DesignVersionStatus,
    JobStatus,
    ModelRunStatus,
)
from caragent_core.generation import create_generation_brief
from caragent_core.models import (
    Artifact,
    DesignVersion,
    GenerationJob,
    JobEvent,
    ModelRun,
    metadata,
)
from caragent_core.services import assets, jobs, workspaces
from caragent_core.storage import InMemoryObjectStorage
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from caragent_worker.config import WorkerSettings
from caragent_worker.providers import (
    ImageGenerationRequest,
    ImageGenerationResult,
    ImageProviderConfigurationError,
    ImageProviderError,
    ImageProviderTimeoutError,
)
from caragent_worker.tasks import jobs as generation_tasks
from caragent_worker.tasks.jobs import run_generate_2d_concept_job


@dataclass(frozen=True)
class SeededGenerationJob:
    database_url: str
    session_factory: async_sessionmaker[AsyncSession]
    job_id: UUID
    parent_version_id: UUID | None = None
    reference_asset_ids: tuple[UUID, ...] = ()


@dataclass(frozen=True)
class GenerationState:
    job: GenerationJob
    events: list[JobEvent]
    model_runs: list[ModelRun]
    artifacts: list[Artifact]
    versions: list[DesignVersion]


def test_generation_worker_persists_prompt_artifact_version_and_success(
    tmp_path: Path,
) -> None:
    seeded = seed_generation_job(tmp_path)
    output_storage = InMemoryObjectStorage()

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            settings=WorkerSettings(),
            storage=output_storage,
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "succeeded"
    assert result["external_calls"] is False
    assert result["artifact_id"] == str(state.artifacts[0].id)
    assert result["version_id"] == str(state.versions[0].id)

    assert state.job.status == JobStatus.SUCCEEDED.value
    assert state.job.latest_error is None
    assert state.job.actual_cost == 0
    assert state.job.estimated_cost == 0
    assert [event.status for event in state.events] == [
        "queued",
        "running",
        "running",
        "running",
        "running",
        "succeeded",
    ]
    assert [event.message for event in state.events][1:] == [
        "Generation worker started.",
        "Prompt planned.",
        "Generated artifact stored.",
        "Design version created.",
        "Generation completed.",
    ]

    assert len(state.model_runs) == 1
    model_run = state.model_runs[0]
    assert model_run.status == ModelRunStatus.SUCCEEDED.value
    assert model_run.provider == "local-deterministic"
    assert model_run.model == "local-concept-v1"
    assert model_run.prompt_text is not None
    assert "2D concept preview" in model_run.prompt_text
    assert model_run.prompt_payload["concept_label"] == "concept_preview"
    assert model_run.output_artifact_id == state.artifacts[0].id

    assert len(state.artifacts) == 1
    artifact = state.artifacts[0]
    stored = output_storage.objects[artifact.object_key]
    assert artifact.kind == ArtifactKind.GENERATED_IMAGE.value
    assert artifact.content_type == "image/png"
    assert artifact.width == 1536
    assert artifact.height == 768
    assert artifact.byte_size == len(stored.content)
    assert artifact.checksum_sha256 == hashlib.sha256(stored.content).hexdigest()
    assert artifact.metadata_json["concept_label"] == "concept_preview"
    assert artifact.metadata_json["overlay_layer_count"] == 1
    assert artifact.metadata_json["safe_zone_count"] >= 5
    assert artifact.metadata_json["warning_count"] == 0
    assert artifact.metadata_json["preview_spec"]["overlay_layers"] == [
        {"id": "text-1", "kind": "text", "text": "MOON DRIVE", "zone_id": "door-main"},
    ]
    assert artifact.metadata_json["preview_spec"]["safe_zones"][0]["id"] == "door-main"

    assert len(state.versions) == 1
    version = state.versions[0]
    assert version.status == DesignVersionStatus.GENERATED.value
    assert version.job_id == state.job.id
    assert version.brief_id == state.job.brief_id
    assert version.parameters["concept_label"] == "concept_preview"
    assert version.parameters["overlay_layer_count"] == 1
    assert version.parameters["preview_spec"]["template"]["id"] == "generic-side-coupe"
    assert version.parameters["preview_spec"]["overlay_layers"][0]["text"] == "MOON DRIVE"
    assert version.parameters["safe_zone_count"] >= 5
    assert version.parameters["warning_count"] == 0
    assert version.parent_version_id is None
    assert version.lineage_depth == 0


def test_generation_worker_creates_child_version_from_iteration_metadata(
    tmp_path: Path,
) -> None:
    seeded = seed_generation_job(tmp_path, iteration_parent=True)
    output_storage = InMemoryObjectStorage()

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            settings=WorkerSettings(),
            storage=output_storage,
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert seeded.parent_version_id is not None
    assert result["status"] == "succeeded"
    assert result["version_id"] == str(state.versions[1].id)

    parent, child = state.versions
    assert parent.id == seeded.parent_version_id
    assert parent.parent_version_id is None
    assert parent.lineage_depth == 0
    assert parent.parameters["concept_label"] == "parent_preview"
    assert parent.parameters["preview_spec"]["overlay_layers"][0]["text"] == "MOON DRIVE"
    assert child.parent_version_id == parent.id
    assert child.lineage_depth == 1
    assert child.parameters["parent_version_id"] == str(parent.id)
    assert child.parameters["change_request"] == "Make the side stripe bolder."
    assert child.parameters["parameter_overrides"] == {"coverage": "door focus"}

    assert state.model_runs[0].parameters["parent_version_id"] == str(parent.id)
    assert state.model_runs[0].parameters["change_request"] == "Make the side stripe bolder."
    assert state.model_runs[0].parameters["parameter_overrides"] == {"coverage": "door focus"}


def test_generation_worker_passes_reference_usage_to_provider_request(
    tmp_path: Path,
) -> None:
    provider = RecordingSuccessProvider()
    seeded = seed_generation_job(
        tmp_path,
        include_confirmed_reference_asset=True,
        reference_role="character",
    )
    reference_id = str(seeded.reference_asset_ids[0])

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "succeeded"
    assert len(provider.requests) == 1
    request = provider.requests[0]
    assert request.input_artifact_ids == [reference_id]
    assert request.reference_usage == {
        "requested": [
            {
                "asset_id": reference_id,
                "enabled": True,
                "role": "character",
                "schema_version": 1,
            },
        ],
        "schema_version": 1,
    }
    assert request.prompt_payload["reference_warning_count"] == 0
    assert request.prompt_payload["included_reference_asset_ids"] == [reference_id]
    assert state.model_runs[0].input_artifact_ids == [reference_id]
    assert state.model_runs[0].prompt_payload["reference_usage"]["items"][0]["asset_id"] == (
        reference_id
    )
    assert state.model_runs[0].prompt_payload["reference_usage"]["items"][0]["rights"][
        "rights_status"
    ] == "confirmed"


def test_generation_worker_persists_reference_trace_across_durable_records(
    tmp_path: Path,
) -> None:
    seeded = seed_generation_job(
        tmp_path,
        include_confirmed_reference_asset=True,
        reference_role="character",
    )
    reference_id = str(seeded.reference_asset_ids[0])
    output_storage = InMemoryObjectStorage()

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            settings=WorkerSettings(),
            storage=output_storage,
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "succeeded"
    surfaces = [
        state.model_runs[0].parameters,
        state.model_runs[0].prompt_payload,
        state.artifacts[0].metadata_json,
        state.versions[0].parameters,
        state.job.metadata_json["operations"],
        state.events[-1].metadata_json,
    ]
    for surface in surfaces:
        assert_reference_trace(surface, reference_id=reference_id)


def test_generation_worker_recomposes_safe_targeted_edit_without_provider_call(
    tmp_path: Path,
) -> None:
    provider = RecordingSuccessProvider()
    seeded = seed_generation_job(
        tmp_path,
        iteration_parent=True,
        targeted_edit_instruction="text=STAR RUN; move up",
    )
    output_storage = InMemoryObjectStorage()

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_provider_calls_enabled=True,
                ai_provider_default="bfl",
                v2_targeted_regeneration_enabled=True,
            ),
            storage=output_storage,
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert seeded.parent_version_id is not None
    assert result["status"] == "succeeded"
    assert result["external_calls"] is False
    assert result["provider"] == "deterministic-recomposition"
    assert result["model"] == "preview-spec-recomposer-v1"
    assert provider.requests == []

    parent, child = state.versions
    assert parent.id == seeded.parent_version_id
    assert child.parent_version_id == parent.id
    assert child.lineage_depth == parent.lineage_depth + 1

    parent_layer = parent.parameters["preview_spec"]["overlay_layers"][0]
    child_layer = child.parameters["preview_spec"]["overlay_layers"][0]
    assert parent_layer == {
        "id": "text-1",
        "kind": "text",
        "text": "MOON DRIVE",
        "zone_id": "door-main",
    }
    assert child_layer["text"] == "STAR RUN"
    assert child_layer["y"] < 0.47
    assert child.parameters["edit_route"] == "deterministic_recomposition"
    assert child.parameters["mask_artifact_id"] == str(state.artifacts[0].id)
    assert child.parameters["mask_content_type"] == "image/png"
    assert child.parameters["prompt_delta"] == {
        "instructions": ["text=STAR RUN; move up"],
        "summary": "text=STAR RUN; move up",
    }
    assert child.parameters["region"]["unit"] == "normalized"
    assert child.parameters["recomposition_route"] == "deterministic_recomposition"
    assert child.parameters["target"] == {"id": "text-1", "type": "overlay_layer"}
    assert set(child.parameters["changed_fields"]) >= {"text", "y"}

    assert len(state.model_runs) == 1
    model_run = state.model_runs[0]
    assert model_run.status == ModelRunStatus.SUCCEEDED.value
    assert model_run.provider == "deterministic-recomposition"
    assert model_run.model == "preview-spec-recomposer-v1"
    assert model_run.parameters["edit_route"] == "deterministic_recomposition"
    assert model_run.parameters["mask_artifact_id"] == str(state.artifacts[0].id)
    assert model_run.parameters["prompt_delta"]["summary"] == "text=STAR RUN; move up"
    assert model_run.parameters["recomposition_route"] == "deterministic_recomposition"
    assert model_run.parameters["parent_version_id"] == str(parent.id)
    assert model_run.prompt_payload["mask_edit"]["edit_route"] == (
        "deterministic_recomposition"
    )
    assert model_run.output_artifact_id == state.artifacts[1].id

    child_artifact = state.artifacts[1]
    assert child_artifact.metadata_json["edit_route"] == "deterministic_recomposition"
    assert child_artifact.metadata_json["mask_artifact_id"] == str(state.artifacts[0].id)
    assert child_artifact.metadata_json["prompt_delta"]["instructions"] == [
        "text=STAR RUN; move up",
    ]
    assert child_artifact.metadata_json["recomposition_route"] == "deterministic_recomposition"
    assert child_artifact.metadata_json["parent_version_id"] == str(parent.id)
    assert child_artifact.metadata_json["target"] == {"id": "text-1", "type": "overlay_layer"}
    assert child_artifact.object_key in output_storage.objects
    start_event = next(
        event for event in state.events if event.message == "Deterministic recomposition started."
    )
    assert start_event.metadata_json["edit_route"] == "deterministic_recomposition"
    assert state.job.metadata_json["operations"]["recomposition_route"] == (
        "deterministic_recomposition"
    )
    assert state.job.metadata_json["operations"]["edit_route"] == "deterministic_recomposition"
    assert state.job.metadata_json["operations"]["mask_artifact_id"] == str(state.artifacts[0].id)


def test_generation_worker_rejects_invalid_recomposition_without_partial_child(
    tmp_path: Path,
) -> None:
    provider = RecordingSuccessProvider()
    seeded = seed_generation_job(
        tmp_path,
        iteration_parent=True,
        targeted_edit_instruction="text=STAR RUN",
        targeted_edit_target_id="missing-layer",
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(v2_targeted_regeneration_enabled=True),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert "target not found" in (state.job.latest_error or "")
    assert provider.requests == []
    assert len(state.versions) == 1
    assert len(state.artifacts) == 1
    assert state.model_runs == []
    assert_failure_metadata(
        state,
        category="targeted_edit_invalid",
        error=state.job.latest_error or "",
        model="preview-spec-recomposer-v1",
        provider="deterministic-recomposition",
        stage="recomposition_validation",
    )
    operations = state.job.metadata_json["operations"]
    assert operations["retry_eligible"] is False
    assert operations["retry_route"] == "deterministic_recomposition"
    assert operations["blocked_reason"] == state.job.latest_error
    assert operations["target"] == {"id": "missing-layer", "type": "overlay_layer"}


def test_generation_worker_blocks_unsupported_provider_mask_route_before_call(
    tmp_path: Path,
) -> None:
    provider = RecordingSuccessProvider()
    seeded = seed_generation_job(
        tmp_path,
        iteration_parent=True,
        model="flux-2-pro-preview",
        provider="bfl",
        provider_parameters={"output_format": "png"},
        targeted_edit_instruction="Repaint the selected door text.",
        targeted_edit_route_preference="provider_masked_generation",
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_hosted_daily_call_limit=10,
                ai_hosted_rate_limit_per_minute=10,
                ai_max_estimated_cost_per_job="1.0000",
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="disabled",
                v2_hosted_provider_rollout_enabled=True,
                v2_targeted_regeneration_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert "provider_masked_generation" in (state.job.latest_error or "")
    assert "does not support" in (state.job.latest_error or "")
    assert provider.requests == []
    assert len(state.versions) == 1
    assert len(state.artifacts) == 1
    assert state.model_runs[0].status == ModelRunStatus.FAILED.value
    assert state.model_runs[0].parameters["edit_route"] == "provider_masked_generation"
    assert_failure_metadata(
        state,
        category="targeted_edit_unsupported",
        error=state.job.latest_error or "",
        model="flux-2-pro-preview",
        provider="bfl",
        stage="provider_mask_preflight",
    )
    assert state.job.metadata_json["operations"]["retry_eligible"] is False
    assert state.job.metadata_json["operations"]["retry_route"] == "provider_masked_generation"
    assert state.job.metadata_json["operations"]["blocked_reason"] == state.job.latest_error


def test_generation_worker_marks_provider_mask_provider_failure_retryable(
    tmp_path: Path,
    monkeypatch: object,
) -> None:
    provider = RaisingProvider(ImageProviderError("bfl-secret failed upstream"))
    seeded = seed_generation_job(
        tmp_path,
        iteration_parent=True,
        model="flux-2-pro-preview",
        provider="bfl",
        provider_parameters={"output_format": "png"},
        targeted_edit_instruction="Repaint the selected door text.",
        targeted_edit_route_preference="provider_masked_generation",
    )

    def allow_provider_mask_route(_provider_name: str, *, settings: WorkerSettings) -> None:
        return None

    monkeypatch.setattr(
        generation_tasks,
        "_require_provider_mask_capability",
        allow_provider_mask_route,
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_hosted_daily_call_limit=10,
                ai_hosted_rate_limit_per_minute=10,
                ai_max_estimated_cost_per_job="1.0000",
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="disabled",
                v2_hosted_provider_rollout_enabled=True,
                v2_targeted_regeneration_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert "[redacted]" in (state.job.latest_error or "")
    assert len(state.versions) == 1
    assert len(state.artifacts) == 1
    assert_failure_metadata(
        state,
        category="provider",
        error="[redacted] failed upstream",
        model="flux-2-pro-preview",
        provider="bfl",
        stage="provider_generate",
    )
    operations = state.job.metadata_json["operations"]
    assert operations["retry_eligible"] is True
    assert operations["retry_route"] == "provider_masked_generation"
    assert operations["blocked_reason"] is None
    assert operations["edit_intent"]["route_preference"] == "provider_masked_generation"
    assert "bfl-secret" not in str(operations)


def test_generation_worker_passes_mask_metadata_to_allowed_mock_provider(
    tmp_path: Path,
    monkeypatch: object,
) -> None:
    provider = RecordingSuccessProvider()
    seeded = seed_generation_job(
        tmp_path,
        iteration_parent=True,
        model="flux-2-pro-preview",
        provider="bfl",
        provider_parameters={"output_format": "png"},
        targeted_edit_instruction="Repaint the selected door text.",
        targeted_edit_route_preference="provider_masked_generation",
    )

    def allow_provider_mask_route(_provider_name: str, *, settings: WorkerSettings) -> None:
        return None

    monkeypatch.setattr(
        generation_tasks,
        "_require_provider_mask_capability",
        allow_provider_mask_route,
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_hosted_daily_call_limit=10,
                ai_hosted_rate_limit_per_minute=10,
                ai_max_estimated_cost_per_job="1.0000",
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="disabled",
                v2_hosted_provider_rollout_enabled=True,
                v2_targeted_regeneration_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "succeeded"
    assert len(provider.requests) == 1
    request = provider.requests[0]
    assert request.provider == "bfl"
    assert request.mask_edit is not None
    assert request.mask_edit.route_preference == "provider_masked_generation"
    assert request.mask_edit.mask_content_type == "image/png"
    assert request.mask_edit.region["unit"] == "normalized"
    assert request.mask_edit.prompt_delta["instructions"] == [
        "Repaint the selected door text.",
    ]
    assert state.model_runs[0].parameters["edit_route"] == "provider_masked_generation"
    assert state.model_runs[0].prompt_payload["mask_edit"]["target"] == {
        "id": "text-1",
        "type": "overlay_layer",
    }
    parent, child = state.versions
    assert child.parent_version_id == parent.id
    assert child.lineage_depth == parent.lineage_depth + 1
    assert parent.parameters["preview_spec"]["overlay_layers"][0]["text"] == "MOON DRIVE"
    assert state.model_runs[0].parameters["mask_artifact_id"] == str(state.artifacts[0].id)
    assert state.model_runs[0].parameters["prompt_delta"]["summary"] == (
        "Repaint the selected door text."
    )
    assert state.artifacts[1].metadata_json["edit_route"] == "provider_masked_generation"
    assert state.versions[1].parameters["edit_route"] == "provider_masked_generation"
    assert state.job.metadata_json["operations"]["edit_route"] == "provider_masked_generation"
    assert state.events[-1].metadata_json["edit_route"] == "provider_masked_generation"


def test_generation_worker_records_sanitized_provider_failure(tmp_path: Path) -> None:
    seeded = seed_generation_job(tmp_path)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=FailingProvider("provider-secret\nfailed upstream"),
            settings=WorkerSettings(ai_provider_bfl_api_key="provider-secret"),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert state.job.status == JobStatus.FAILED.value
    assert state.job.latest_error == "[redacted] failed upstream"
    assert state.model_runs[0].status == ModelRunStatus.FAILED.value
    assert state.model_runs[0].error_message == "[redacted] failed upstream"
    assert_failure_metadata(
        state,
        category="provider",
        error="[redacted] failed upstream",
        stage="provider_generate",
    )
    assert "provider-secret" not in str(state.job.metadata_json)
    assert "provider-secret" not in str(state.events[-1].metadata_json)
    assert state.artifacts == []
    assert state.versions == []


def test_generation_worker_maps_provider_status_to_failure_kind(
    tmp_path: Path,
) -> None:
    seeded = seed_generation_job(
        tmp_path,
        provider="bfl",
        model="flux-2-pro-preview",
        provider_parameters={"output_format": "png"},
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=RaisingProvider(
                ImageProviderError(
                    "bfl-secret rejected by policy",
                    provider_status="request_moderated",
                ),
            ),
            settings=WorkerSettings(
                ai_hosted_daily_call_limit=10,
                ai_hosted_rate_limit_per_minute=10,
                ai_max_estimated_cost_per_job="1.0000",
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="disabled",
                v2_hosted_provider_rollout_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    operations = state.job.metadata_json["operations"]
    assert operations["failure_category"] == "provider"
    assert operations["provider_status"] == "request_moderated"
    assert operations["provider_failure_kind"] == "moderation"
    assert operations["error"] == "[redacted] rejected by policy"
    assert "bfl-secret" not in str(operations)


def test_generation_worker_classifies_provider_timeout_failure(tmp_path: Path) -> None:
    seeded = seed_generation_job(tmp_path)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=RaisingProvider(ImageProviderTimeoutError("provider timed out")),
            settings=WorkerSettings(),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert state.job.latest_error == "provider timed out"
    assert state.model_runs[0].error_message == "provider timed out"
    assert_failure_metadata(
        state,
        category="timeout",
        error="provider timed out",
        stage="provider_generate",
    )


def test_generation_worker_retries_transient_provider_failure_before_success(
    tmp_path: Path,
) -> None:
    provider = FlakyThenSuccessProvider([ImageProviderTimeoutError("first timeout")])
    seeded = seed_generation_job(tmp_path)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(ai_generation_max_attempts=2),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "succeeded"
    assert result["provider"] == "local-deterministic"
    assert provider.calls == 2
    assert [model_run.status for model_run in state.model_runs] == [
        ModelRunStatus.FAILED.value,
        ModelRunStatus.SUCCEEDED.value,
    ]
    assert state.model_runs[0].error_message == "first timeout"
    assert state.model_runs[0].parameters["provider_attempt"] == 1
    assert state.model_runs[1].parameters["provider_attempt"] == 2
    assert state.artifacts[0].metadata_json["provider_attempt_count"] == 2
    assert state.versions[0].parameters["provider_attempt_count"] == 2
    assert state.job.metadata_json["operations"]["provider_attempt_count"] == 2


def test_generation_worker_falls_back_to_local_provider_after_hosted_failure(
    tmp_path: Path,
) -> None:
    provider = CountingRaisingProvider(ImageProviderError("hosted upstream failed"))
    seeded = seed_generation_job(tmp_path)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_generation_max_attempts=1,
                ai_hosted_daily_call_limit=10,
                ai_hosted_rate_limit_per_minute=10,
                ai_local_image_height=64,
                ai_local_image_width=128,
                ai_max_estimated_cost_per_job="1.0000",
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="bfl",
                ai_provider_fallback_enabled=True,
                ai_provider_fallback_name="local-deterministic",
                v2_hosted_provider_rollout_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "succeeded"
    assert result["provider"] == "local-deterministic"
    assert result["external_calls"] is False
    assert provider.calls == 1
    assert [model_run.status for model_run in state.model_runs] == [
        ModelRunStatus.FAILED.value,
        ModelRunStatus.SUCCEEDED.value,
    ]
    assert state.model_runs[0].provider == "bfl"
    assert state.model_runs[0].error_message == "hosted upstream failed"
    assert state.model_runs[1].provider == "local-deterministic"
    assert state.artifacts[0].width == 128
    assert state.artifacts[0].height == 64

    for output_metadata in (
        state.artifacts[0].metadata_json,
        state.versions[0].parameters,
        state.job.metadata_json["operations"],
    ):
        assert output_metadata["fallback_from_provider"] == "bfl"
        assert output_metadata["fallback_to_provider"] == "local-deterministic"
        assert output_metadata["fallback_reason"] == "hosted upstream failed"
        assert output_metadata["provider_attempt_count"] == 2
    assert any(
        event.message == "Fallback provider started."
        and event.metadata_json["fallback_from_provider"] == "bfl"
        and event.metadata_json["fallback_to_provider"] == "local-deterministic"
        for event in state.events
    )


def test_generation_worker_blocks_hosted_call_when_quota_guards_are_missing(
    tmp_path: Path,
) -> None:
    provider = FlakyThenSuccessProvider([])
    seeded = seed_generation_job(tmp_path)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="bfl",
                v2_hosted_provider_rollout_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert provider.calls == 0
    assert len(state.model_runs) == 1
    assert state.model_runs[0].status == ModelRunStatus.FAILED.value
    assert state.model_runs[0].error_message == (
        "Hosted calls require daily, per-minute, and per-job cost limits."
    )
    assert_failure_metadata(
        state,
        category="provider_configuration",
        error="Hosted calls require daily, per-minute, and per-job cost limits.",
        provider="bfl",
        stage="hosted_preflight",
    )


def test_generation_worker_uses_persisted_hosted_intent_over_process_default(
    tmp_path: Path,
) -> None:
    provider = RecordingSuccessProvider()
    seeded = seed_generation_job(
        tmp_path,
        provider="bfl",
        model="flux-2-pro-preview",
        provider_parameters={"output_format": "png"},
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_hosted_daily_call_limit=10,
                ai_hosted_rate_limit_per_minute=10,
                ai_max_estimated_cost_per_job="1.0000",
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="disabled",
                ai_provider_model="local-concept-v1",
                v2_hosted_provider_rollout_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "succeeded"
    assert result["provider"] == "bfl"
    assert provider.requests[0].provider == "bfl"
    assert provider.requests[0].model == "flux-2-pro-preview"
    assert provider.requests[0].parameters["output_format"] == "png"
    assert state.model_runs[0].provider == "bfl"
    assert state.model_runs[0].model == "flux-2-pro-preview"
    assert state.model_runs[0].parameters["provider_route"] == "bfl"
    assert state.artifacts[0].metadata_json["external_calls"] is True


def test_generation_worker_persists_hosted_trace_and_actual_cost(
    tmp_path: Path,
) -> None:
    provider = CostedProvider(actual_cost=Decimal("0.0300"))
    seeded = seed_generation_job(
        tmp_path,
        provider="bfl",
        model="flux-2-pro-preview",
        provider_parameters={"output_format": "png"},
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_hosted_daily_call_limit=10,
                ai_hosted_rate_limit_per_minute=10,
                ai_max_estimated_cost_per_job="1.0000",
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="disabled",
                v2_hosted_provider_rollout_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "succeeded"
    assert state.job.provider == "bfl"
    assert state.job.model == "flux-2-pro-preview"
    assert state.job.estimated_cost is None
    assert state.job.actual_cost == Decimal("0.0300")

    model_run = state.model_runs[0]
    assert model_run.provider == "bfl"
    assert model_run.model == "flux-2-pro-preview"
    assert model_run.actual_cost == Decimal("0.0300")
    assert model_run.estimated_cost is None
    assert model_run.parameters["output_format"] == "png"
    assert model_run.prompt_payload["provider"] == "bfl"
    assert model_run.prompt_payload["model"] == "flux-2-pro-preview"
    assert model_run.input_artifact_ids == []

    artifact_metadata = state.artifacts[0].metadata_json
    assert artifact_metadata["provider"] == "bfl"
    assert artifact_metadata["model"] == "flux-2-pro-preview"
    assert artifact_metadata["actual_cost"] == "0.0300"
    assert artifact_metadata["provider_status"] == "ready"
    assert "signed-secret" not in str(artifact_metadata)

    version_parameters = state.versions[0].parameters
    assert version_parameters["provider"] == "bfl"
    assert version_parameters["model"] == "flux-2-pro-preview"
    assert version_parameters["actual_cost"] == "0.0300"


def test_generation_worker_rechecks_hosted_preflight_for_persisted_intent(
    tmp_path: Path,
) -> None:
    provider = RecordingSuccessProvider()
    seeded = seed_generation_job(
        tmp_path,
        provider="bfl",
        model="flux-2-pro-preview",
        provider_parameters={"output_format": "png"},
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="disabled",
                v2_hosted_provider_rollout_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert provider.requests == []
    assert state.model_runs[0].provider == "bfl"
    assert_failure_metadata(
        state,
        category="provider_configuration",
        error="Hosted calls require daily, per-minute, and per-job cost limits.",
        model="flux-2-pro-preview",
        provider="bfl",
        stage="hosted_preflight",
    )


def test_generation_worker_rejects_unsupported_persisted_provider_before_call(
    tmp_path: Path,
) -> None:
    provider = RecordingSuccessProvider()
    seeded = seed_generation_job(
        tmp_path,
        provider="not-real",
        model="not-real-model",
        provider_parameters={"output_format": "png"},
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(ai_provider_calls_enabled=True),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert provider.requests == []
    assert state.model_runs == []
    assert_failure_metadata(
        state,
        category="provider_configuration",
        error="Unsupported image provider: not-real",
        model="not-real-model",
        provider="not-real",
        stage="prompt_plan",
    )


def test_generation_worker_blocks_hosted_call_when_daily_quota_is_reached(
    tmp_path: Path,
) -> None:
    provider = FlakyThenSuccessProvider([])
    seeded = seed_generation_job(tmp_path)
    asyncio.run(seed_prior_hosted_model_runs(seeded.session_factory, seeded.job_id, count=1))

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_hosted_daily_call_limit=1,
                ai_hosted_rate_limit_per_minute=10,
                ai_max_estimated_cost_per_job="1.0000",
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="bfl",
                v2_hosted_provider_rollout_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert provider.calls == 0
    assert state.model_runs[-1].error_message == "Hosted provider daily call limit reached."
    assert_failure_metadata(
        state,
        category="provider_configuration",
        error="Hosted provider daily call limit reached.",
        provider="bfl",
        stage="hosted_preflight",
    )


def test_generation_worker_blocks_hosted_call_when_rate_limit_is_reached(
    tmp_path: Path,
) -> None:
    provider = FlakyThenSuccessProvider([])
    seeded = seed_generation_job(tmp_path)
    asyncio.run(seed_prior_hosted_model_runs(seeded.session_factory, seeded.job_id, count=1))

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_hosted_daily_call_limit=10,
                ai_hosted_rate_limit_per_minute=1,
                ai_max_estimated_cost_per_job="1.0000",
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="bfl",
                v2_hosted_provider_rollout_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert provider.calls == 0
    assert state.model_runs[-1].error_message == (
        "Hosted provider per-minute rate limit reached."
    )
    assert_failure_metadata(
        state,
        category="provider_configuration",
        error="Hosted provider per-minute rate limit reached.",
        provider="bfl",
        stage="hosted_preflight",
    )


def test_generation_worker_local_generation_bypasses_hosted_quota_controls(
    tmp_path: Path,
) -> None:
    seeded = seed_generation_job(tmp_path)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            settings=WorkerSettings(),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "succeeded"
    assert result["external_calls"] is False
    assert state.job.actual_cost == 0
    assert state.job.estimated_cost == 0
    assert state.model_runs[0].provider == "local-deterministic"


def test_generation_worker_classifies_provider_configuration_failure(
    tmp_path: Path,
) -> None:
    seeded = seed_generation_job(tmp_path)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=RaisingProvider(
                ImageProviderConfigurationError("bfl-secret missing provider config"),
            ),
            settings=WorkerSettings(ai_provider_bfl_api_key="bfl-secret"),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert state.job.latest_error == "[redacted] missing provider config"
    assert_failure_metadata(
        state,
        category="provider_configuration",
        error="[redacted] missing provider config",
        stage="provider_generate",
    )
    assert "bfl-secret" not in str(state.job.metadata_json)


def test_generation_worker_does_not_retry_or_fallback_provider_configuration_failure(
    tmp_path: Path,
) -> None:
    provider = CountingRaisingProvider(ImageProviderConfigurationError("bad provider config"))
    seeded = seed_generation_job(tmp_path)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_generation_max_attempts=3,
                ai_provider_fallback_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert provider.calls == 1
    assert len(state.model_runs) == 1
    assert_failure_metadata(
        state,
        category="provider_configuration",
        error="bad provider config",
        stage="provider_generate",
    )


def test_generation_worker_classifies_storage_failure(tmp_path: Path) -> None:
    seeded = seed_generation_job(tmp_path)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            settings=WorkerSettings(),
            storage=FailingObjectStorage("disk write failed"),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert state.job.latest_error == "disk write failed"
    assert state.model_runs[0].status == ModelRunStatus.FAILED.value
    assert_failure_metadata(
        state,
        category="storage",
        error="disk write failed",
        stage="storage_put",
    )
    assert state.artifacts == []
    assert state.versions == []


def test_generation_worker_blocks_missing_rights_before_provider_execution(
    tmp_path: Path,
) -> None:
    provider = RecordingProvider()
    seeded = seed_generation_job(tmp_path, include_missing_rights_asset=True)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(ai_generation_max_attempts=3),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert provider.called is False
    assert state.job.status == JobStatus.FAILED.value
    assert "Asset rights are not confirmed" in (state.job.latest_error or "")
    assert len(state.model_runs) == 1
    assert state.model_runs[0].status == ModelRunStatus.FAILED.value
    assert_failure_metadata(
        state,
        category="validation_rights",
        error=state.job.latest_error or "",
        stage="rights_check",
    )


def test_generation_worker_blocks_missing_logo_rights_before_provider_execution(
    tmp_path: Path,
) -> None:
    provider = RecordingProvider()
    seeded = seed_generation_job(tmp_path, include_missing_logo_rights_asset=True)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert provider.called is False
    assert state.job.status == JobStatus.FAILED.value
    assert "Asset rights are not confirmed" in (state.job.latest_error or "")
    assert state.model_runs[0].status == ModelRunStatus.FAILED.value
    assert_failure_metadata(
        state,
        category="validation_rights",
        error=state.job.latest_error or "",
        stage="rights_check",
    )


def test_generation_worker_requires_structured_reference_rights_before_provider_call(
    tmp_path: Path,
) -> None:
    provider = RecordingSuccessProvider()
    seeded = seed_generation_job(
        tmp_path,
        include_missing_structured_reference_asset=True,
        reference_role="character",
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert provider.requests == []
    assert "Asset rights are not confirmed" in (state.job.latest_error or "")
    assert state.model_runs[0].status == ModelRunStatus.FAILED.value
    assert_failure_metadata(
        state,
        category="validation_rights",
        error=state.job.latest_error or "",
        stage="rights_check",
    )


def test_generation_worker_blocks_bfl_reference_roles_before_provider_call(
    tmp_path: Path,
) -> None:
    provider = RecordingSuccessProvider()
    seeded = seed_generation_job(
        tmp_path,
        include_confirmed_reference_asset=True,
        model="flux-2-pro-preview",
        provider="bfl",
        provider_parameters={"output_format": "png"},
        reference_role="character",
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(
                ai_hosted_daily_call_limit=10,
                ai_hosted_rate_limit_per_minute=10,
                ai_max_estimated_cost_per_job="1.0000",
                ai_provider_bfl_api_key="bfl-secret",
                ai_provider_calls_enabled=True,
                ai_provider_default="disabled",
                v2_hosted_provider_rollout_enabled=True,
                v2_reference_guidance_enabled=True,
            ),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "failed"
    assert provider.requests == []
    assert "Reference image input is not verified" in (state.job.latest_error or "")
    assert_failure_metadata(
        state,
        category="provider_configuration",
        error=state.job.latest_error or "",
        model="flux-2-pro-preview",
        provider="bfl",
        stage="reference_capability_preflight",
    )
    operations = state.job.metadata_json["operations"]
    assert operations["reference_warning_count"] == 1
    assert operations["unsupported_reference_roles"] == ["character"]
    assert operations["reference_warnings"] == [
        {
            "asset_id": str(seeded.reference_asset_ids[0]),
            "reason": "unsupported_by_provider",
            "role": "character",
        },
    ]


def test_generation_worker_skips_already_canceled_job_before_provider(
    tmp_path: Path,
) -> None:
    provider = RecordingProvider()
    seeded = seed_generation_job(tmp_path)
    asyncio.run(cancel_seeded_job(seeded.session_factory, seeded.job_id, reason="user_request"))

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result == {
        "external_calls": False,
        "job_id": str(seeded.job_id),
        "status": "canceled",
    }
    assert provider.called is False
    assert state.job.status == JobStatus.CANCELED.value
    assert state.job.latest_error is None
    assert state.job.metadata_json["operations"] == {
        "failure_category": "canceled",
        "reason": "user_request",
    }
    assert state.model_runs == []
    assert state.artifacts == []
    assert state.versions == []
    assert state.events[-1].metadata_json["failure_category"] == "canceled"
    assert state.events[-1].metadata_json["stage"] == "worker_start"


def test_generation_worker_stops_when_canceled_before_provider_execution(
    tmp_path: Path,
    monkeypatch: object,
) -> None:
    provider = RecordingProvider()
    seeded = seed_generation_job(tmp_path)

    async def cancel_during_rights_check(
        session: AsyncSession,
        _workspace_id: UUID,
        _reference_asset_ids: list[str],
    ) -> None:
        await jobs.cancel_job(
            session,
            seeded.job_id,
            reason="after_prompt",
            source="test",
        )

    monkeypatch.setattr(
        generation_tasks,
        "_require_confirmed_reference_rights",
        cancel_during_rights_check,
    )

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "canceled"
    assert result["external_calls"] is False
    assert provider.called is False
    assert state.job.status == JobStatus.CANCELED.value
    assert state.model_runs[0].status == ModelRunStatus.FAILED.value
    assert state.model_runs[0].error_message == "Job canceled."
    assert state.artifacts == []
    assert state.versions == []
    assert state.events[-1].metadata_json["failure_category"] == "canceled"
    assert state.events[-1].metadata_json["stage"] == "after_rights_check"


def test_generation_worker_does_not_overwrite_canceled_job_after_provider_returns(
    tmp_path: Path,
    monkeypatch: object,
) -> None:
    provider = SuccessfulCancelingProvider()
    seeded = seed_generation_job(tmp_path)
    original_cancel_check = generation_tasks._return_if_canceled

    async def cancel_after_provider(
        session: AsyncSession,
        job_id: UUID,
        *,
        external_calls: bool,
        model_run_id: UUID | None = None,
        stage: str,
    ) -> dict[str, object] | None:
        if stage == "after_provider":
            await jobs.cancel_job(
                session,
                job_id,
                reason="provider_in_flight",
                source="test",
            )
        return await original_cancel_check(
            session,
            job_id,
            external_calls=external_calls,
            model_run_id=model_run_id,
            stage=stage,
        )

    monkeypatch.setattr(generation_tasks, "_return_if_canceled", cancel_after_provider)

    result = asyncio.run(
        run_generate_2d_concept_job(
            seeded.database_url,
            seeded.job_id,
            provider=provider,
            settings=WorkerSettings(),
            storage=InMemoryObjectStorage(),
        ),
    )
    state = asyncio.run(read_generation_state(seeded.session_factory, seeded.job_id))

    assert result["status"] == "canceled"
    assert result["external_calls"] is True
    assert provider.called is True
    assert state.job.status == JobStatus.CANCELED.value
    assert state.model_runs[0].status == ModelRunStatus.FAILED.value
    assert state.model_runs[0].error_message == "Job canceled."
    assert state.artifacts == []
    assert state.versions == []
    assert state.events[-1].metadata_json["failure_category"] == "canceled"
    assert state.events[-1].metadata_json["stage"] == "after_provider"


class FailingProvider:
    def __init__(self, message: str) -> None:
        self.message = message

    async def generate(self, _request: ImageGenerationRequest) -> object:
        raise ImageProviderError(self.message)


class RecordingProvider:
    def __init__(self) -> None:
        self.called = False

    async def generate(self, _request: ImageGenerationRequest) -> object:
        self.called = True
        raise ImageProviderTimeoutError("should not be called")


class CountingRaisingProvider:
    def __init__(self, exc: Exception) -> None:
        self.calls = 0
        self.exc = exc

    async def generate(self, _request: ImageGenerationRequest) -> object:
        self.calls += 1
        raise self.exc


class FlakyThenSuccessProvider:
    def __init__(self, failures: list[Exception]) -> None:
        self.calls = 0
        self.failures = list(failures)

    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        self.calls += 1
        if self.failures:
            raise self.failures.pop(0)
        return provider_result_from_request(request, external_calls=True)


class SuccessfulCancelingProvider:
    def __init__(self) -> None:
        self.called = False

    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        self.called = True
        return provider_result_from_request(request, external_calls=True)


class RecordingSuccessProvider:
    def __init__(self) -> None:
        self.requests: list[ImageGenerationRequest] = []

    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        self.requests.append(request)
        return provider_result_from_request(request, external_calls=True)


class CostedProvider:
    def __init__(self, *, actual_cost: Decimal | None) -> None:
        self.actual_cost = actual_cost

    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        return ImageGenerationResult(
            actual_cost=self.actual_cost,
            content_type="image/png",
            estimated_cost=request.estimated_cost,
            height=1,
            image_bytes=b"\x89PNG\r\n\x1a\n" + b"provider-result",
            metadata={"external_calls": True, "provider_status": "ready"},
            model=request.model,
            provider=request.provider,
            width=1,
        )


def provider_result_from_request(
    request: ImageGenerationRequest,
    *,
    external_calls: bool,
) -> ImageGenerationResult:
    return ImageGenerationResult(
        actual_cost=request.estimated_cost,
        content_type="image/png",
        estimated_cost=request.estimated_cost,
        height=1,
        image_bytes=b"\x89PNG\r\n\x1a\n" + b"provider-result",
        metadata={"external_calls": external_calls},
        model=request.model,
        provider=request.provider,
        width=1,
    )


class RaisingProvider:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    async def generate(self, _request: ImageGenerationRequest) -> object:
        raise self.exc


class FailingObjectStorage:
    def __init__(self, message: str) -> None:
        self.message = message

    async def put_object(self, _key: str, _content: bytes, _content_type: str) -> None:
        raise OSError(self.message)


def assert_failure_metadata(
    state: GenerationState,
    *,
    category: str,
    error: str,
    stage: str,
    model: str = "local-concept-v1",
    provider: str = "local-deterministic",
) -> None:
    operations = state.job.metadata_json["operations"]
    assert operations["error"] == error
    assert operations["failure_category"] == category
    assert operations["model"] == model
    assert operations["provider"] == provider
    assert operations["stage"] == stage
    assert operations["worker_version"] == "0.1.0"
    assert state.events[-1].metadata_json == operations


def assert_reference_trace(surface: dict[str, object], *, reference_id: str) -> None:
    assert surface["included_reference_asset_ids"] == [reference_id]
    assert surface["omitted_reference_asset_ids"] == []
    assert surface["unsupported_reference_roles"] == []
    assert surface["reference_warning_count"] == 0
    assert surface["reference_roles"] == {"character": [reference_id]}
    rights_snapshot = surface["rights_snapshot"]
    assert isinstance(rights_snapshot, dict)
    rights = rights_snapshot[reference_id]
    assert surface["reference_usage"] == {
        "items": [
            {
                "asset_id": reference_id,
                "enabled": True,
                "rights": rights,
                "role": "character",
                "schema_version": 1,
            },
        ],
        "schema_version": 1,
    }
    assert set(rights) == {
        "asset_id",
        "checksum_sha256",
        "content_type",
        "object_key",
        "original_filename",
        "rights_confirmed_at",
        "rights_notes",
        "rights_status",
        "schema_version",
        "source_label",
        "source_url",
    }
    assert rights["asset_id"] == reference_id
    assert rights["checksum_sha256"] == hashlib.sha256(
        b"\x89PNG\r\n\x1a\nstructured-reference",
    ).hexdigest()
    assert rights["content_type"] == "image/png"
    assert str(rights["object_key"]).endswith(
        f"/reference/{reference_id}/structured-reference.png",
    )
    assert rights["original_filename"] == "structured-reference.png"
    assert rights["rights_confirmed_at"] is not None
    assert rights["rights_status"] == "confirmed"
    assert rights["schema_version"] == 1
    assert rights["source_label"] == "licensed reference pack"
    rendered = json.dumps(surface, sort_keys=True)
    assert "image_bytes" not in rendered
    assert "api_key" not in rendered.lower()
    assert "secret" not in rendered.lower()


def seed_generation_job(
    tmp_path: Path,
    *,
    include_confirmed_reference_asset: bool = False,
    include_missing_logo_rights_asset: bool = False,
    include_missing_rights_asset: bool = False,
    include_missing_structured_reference_asset: bool = False,
    iteration_parent: bool = False,
    model: str | None = None,
    provider: str | None = None,
    provider_parameters: dict[str, object] | None = None,
    reference_role: str = "inspiration",
    targeted_edit_instruction: str | None = None,
    targeted_edit_route_preference: str = "deterministic_recomposition",
    targeted_edit_target_id: str = "text-1",
) -> SeededGenerationJob:
    database_url = f"sqlite+aiosqlite:///{(tmp_path / 'generation.db').as_posix()}"
    engine = create_engine(database_url)
    session_factory = create_session_factory(engine)
    job_id, parent_version_id, reference_asset_ids = asyncio.run(
        seed_database(
            engine,
            session_factory,
            include_confirmed_reference_asset=include_confirmed_reference_asset,
            include_missing_logo_rights_asset=include_missing_logo_rights_asset,
            include_missing_rights_asset=include_missing_rights_asset,
            include_missing_structured_reference_asset=include_missing_structured_reference_asset,
            iteration_parent=iteration_parent,
            model=model,
            provider=provider,
            provider_parameters=provider_parameters,
            reference_role=reference_role,
            targeted_edit_instruction=targeted_edit_instruction,
            targeted_edit_route_preference=targeted_edit_route_preference,
            targeted_edit_target_id=targeted_edit_target_id,
        ),
    )
    asyncio.run(engine.dispose())
    return SeededGenerationJob(
        database_url=database_url,
        job_id=job_id,
        parent_version_id=parent_version_id,
        reference_asset_ids=reference_asset_ids,
        session_factory=session_factory,
    )


async def seed_database(
    engine: AsyncEngine,
    session_factory: async_sessionmaker[AsyncSession],
    *,
    include_confirmed_reference_asset: bool,
    include_missing_logo_rights_asset: bool,
    include_missing_rights_asset: bool,
    include_missing_structured_reference_asset: bool,
    iteration_parent: bool,
    model: str | None,
    provider: str | None,
    provider_parameters: dict[str, object] | None,
    reference_role: str,
    targeted_edit_instruction: str | None,
    targeted_edit_route_preference: str,
    targeted_edit_target_id: str,
) -> tuple[UUID, UUID | None, tuple[UUID, ...]]:
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)

    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Generation")
        overlay_logo_asset_ids: list[str] = []
        reference_asset_ids: list[str] = []
        reference_asset_uuids: list[UUID] = []
        reference_usage: list[dict[str, object]] = []
        if include_missing_rights_asset:
            asset = await assets.create_asset(
                session,
                InMemoryObjectStorage(),
                workspace.id,
                byte_content=b"\x89PNG\r\n\x1a\nreference",
                content_type="image/png",
                filename="reference.png",
                kind=AssetKind.REFERENCE.value,
            )
            reference_asset_ids.append(str(asset.id))
            reference_asset_uuids.append(asset.id)
        if include_confirmed_reference_asset or include_missing_structured_reference_asset:
            asset = await assets.create_asset(
                session,
                InMemoryObjectStorage(),
                workspace.id,
                byte_content=b"\x89PNG\r\n\x1a\nstructured-reference",
                content_type="image/png",
                filename="structured-reference.png",
                kind=AssetKind.REFERENCE.value,
            )
            if include_confirmed_reference_asset:
                await assets.update_asset_rights(
                    session,
                    asset.id,
                    rights_status="confirmed",
                    source_label="licensed reference pack",
                )
            reference_asset_uuids.append(asset.id)
            reference_usage.append(
                {
                    "asset_id": str(asset.id),
                    "enabled": True,
                    "role": reference_role,
                    "schema_version": 1,
                },
            )
        if include_missing_logo_rights_asset:
            logo_asset = await assets.create_asset(
                session,
                InMemoryObjectStorage(),
                workspace.id,
                byte_content=b"\x89PNG\r\n\x1a\nlogo",
                content_type="image/png",
                filename="logo.png",
                kind=AssetKind.LOGO.value,
            )
            overlay_logo_asset_ids.append(str(logo_asset.id))

        brief_payload = create_generation_brief(
            original_request="White coupe with Sakura heroine and MOON DRIVE door text.",
            character_theme="Sakura heroine",
            overlay_logo_asset_ids=overlay_logo_asset_ids,
            palette=["white", "teal"],
            reference_asset_ids=reference_asset_ids,
            reference_usage=reference_usage,
            text=["MOON DRIVE"],
        ).model_dump(mode="json")
        brief = await workspaces.create_design_brief(
            session,
            workspace.id,
            payload=brief_payload,
            title="Generation brief",
        )
        parent_version_id: UUID | None = None
        parent_artifact_id: UUID | None = None
        if iteration_parent:
            parent_parameters = parent_version_parameters()
            parent = await jobs.create_design_version(
                session,
                workspace.id,
                brief_id=brief.id,
                parameters=parent_parameters,
                status=DesignVersionStatus.GENERATED.value,
                summary="Parent concept.",
                title="Parent concept",
            )
            parent_version_id = parent.id
            parent_artifact = await jobs.create_artifact(
                session,
                workspace.id,
                byte_size=len(PARENT_IMAGE_BYTES),
                checksum_sha256=hashlib.sha256(PARENT_IMAGE_BYTES).hexdigest(),
                content_type="image/png",
                height=768,
                kind=ArtifactKind.GENERATED_IMAGE.value,
                metadata={
                    **parent_parameters,
                    "preview_spec": parent_parameters["preview_spec"],
                },
                object_key=f"workspaces/{workspace.id}/generated_image/{parent.id}/parent.png",
                version_id=parent.id,
                width=1536,
            )
            parent_artifact_id = parent_artifact.id
        job_metadata = (
            {
                "change_request": "Make the side stripe bolder.",
                "iteration": True,
                "parameter_overrides": {"coverage": "door focus"},
                "parent_version_id": str(parent_version_id),
                "source": "generation-iteration-api",
            }
            if parent_version_id is not None
            else {}
        )
        if targeted_edit_instruction is not None:
            if parent_version_id is None or parent_artifact_id is None:
                raise AssertionError("Targeted edit test jobs require an iteration parent")
            job_metadata["edit_intent"] = targeted_edit_intent_metadata(
                parent_artifact_id=parent_artifact_id,
                parent_version_id=parent_version_id,
                route_preference=targeted_edit_route_preference,
                target_id=targeted_edit_target_id,
                instruction=targeted_edit_instruction,
            )
        if provider is not None or model is not None or provider_parameters:
            job_metadata["provider_intent"] = {
                "model": model,
                "parameters": provider_parameters or {},
                "provider": provider,
            }
        created = await jobs.create_job(
            session,
            workspace.id,
            brief_id=brief.id,
            idempotency_key="generation-001",
            metadata=job_metadata or None,
            model=model,
            operation="generate_2d_concept",
            provider=provider,
        )
        return created.job.id, parent_version_id, tuple(reference_asset_uuids)


def targeted_edit_intent_metadata(
    *,
    parent_artifact_id: UUID,
    parent_version_id: UUID,
    target_id: str,
    instruction: str,
    route_preference: str = "deterministic_recomposition",
) -> dict[str, object]:
    return {
        "mask": {
            "artifact_id": str(parent_artifact_id),
            "content_type": "image/png",
            "height": 768,
            "width": 1536,
        },
        "mode": "targeted_edit",
        "parent_version_id": str(parent_version_id),
        "prompt_delta": {
            "instructions": [instruction],
            "summary": instruction,
        },
        "region": {
            "height": 0.24,
            "type": "rectangle",
            "unit": "normalized",
            "width": 0.34,
            "x": 0.32,
            "y": 0.47,
        },
        "route_preference": route_preference,
        "schema_version": 1,
        "target": {"id": target_id, "type": "overlay_layer"},
    }


def parent_version_parameters() -> dict[str, object]:
    preview_spec = parent_preview_spec()
    return {
        "concept_label": "parent_preview",
        "model": "local-concept-v1",
        "overlay_layer_count": 2,
        "preview_spec": preview_spec,
        "provider": "local-deterministic",
        "safe_zone_count": 2,
        "warning_count": 0,
    }


def parent_preview_spec() -> dict[str, object]:
    return {
        "canvas": {"height": 768, "width": 1536},
        "overlay_layers": [
            {"id": "text-1", "kind": "text", "text": "MOON DRIVE", "zone_id": "door-main"},
            {"asset_id": "logo-1", "id": "logo-1", "kind": "logo", "zone_id": "rear-quarter"},
        ],
        "safe_zones": [
            {
                "height": 0.24,
                "id": "door-main",
                "kind": "body",
                "label": "Door / main side panel",
                "width": 0.34,
                "x": 0.32,
                "y": 0.47,
            },
            {
                "height": 0.2,
                "id": "rear-quarter",
                "kind": "body",
                "label": "Rear quarter panel",
                "width": 0.18,
                "x": 0.64,
                "y": 0.43,
            },
        ],
        "template": {
            "id": "generic-side-coupe",
            "label": "Generic side-view coupe",
            "view": "side",
        },
        "warnings": [],
    }


PARENT_IMAGE_BYTES = b"\x89PNG\r\n\x1a\n" + b"parent-preview"


async def cancel_seeded_job(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: UUID,
    *,
    reason: str,
) -> None:
    async with session_scope(session_factory) as session:
        await jobs.cancel_job(
            session,
            job_id,
            reason=reason,
            source="test",
        )


async def seed_prior_hosted_model_runs(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: UUID,
    *,
    count: int,
) -> None:
    async with session_scope(session_factory) as session:
        for index in range(count):
            await jobs.create_model_run(
                session,
                job_id,
                model=f"hosted-model-{index}",
                parameters={"seeded_usage": True},
                provider="bfl",
                status=ModelRunStatus.FAILED.value,
            )


async def read_generation_state(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: UUID,
) -> GenerationState:
    async with session_scope(session_factory) as session:
        job = await jobs.get_job(session, job_id)
        events = await jobs.list_job_events(session, job_id)
        model_runs = await jobs.list_job_model_runs(session, job_id)
        artifacts = await jobs.list_workspace_artifacts(session, job.workspace_id)
        versions = await jobs.list_workspace_versions(session, job.workspace_id)
    return GenerationState(
        artifacts=artifacts,
        events=events,
        job=job,
        model_runs=model_runs,
        versions=versions,
    )
