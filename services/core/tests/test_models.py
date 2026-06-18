from __future__ import annotations

from sqlalchemy import LargeBinary, UniqueConstraint

from caragent_core import enums
from caragent_core.models import (
    Artifact,
    Asset,
    GenerationJob,
    metadata,
)


def test_domain_enums_include_required_phase_2_states() -> None:
    assert {status.value for status in enums.JobStatus} >= {
        "queued",
        "running",
        "succeeded",
        "failed",
        "canceled",
    }
    assert enums.RightsStatus.MISSING.value == "missing"
    assert enums.RightsStatus.CONFIRMED.value == "confirmed"


def test_metadata_contains_all_phase_2_ledger_tables() -> None:
    assert set(metadata.tables) >= {
        "workspaces",
        "messages",
        "design_briefs",
        "assets",
        "generation_jobs",
        "job_events",
        "design_versions",
        "artifacts",
        "model_runs",
        "feedback",
        "exports",
    }


def test_generation_jobs_have_workspace_scoped_idempotency_constraint() -> None:
    constraints = [
        constraint
        for constraint in GenerationJob.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    assert any(
        {column.name for column in constraint.columns} == {"workspace_id", "idempotency_key"}
        for constraint in constraints
    )


def test_artifacts_and_assets_use_unique_object_keys_without_binary_columns() -> None:
    assert Asset.__table__.c.object_key.unique is True
    assert Artifact.__table__.c.object_key.unique is True

    for table in [Asset.__table__, Artifact.__table__]:
        assert all(not isinstance(column.type, LargeBinary) for column in table.columns)


def test_assets_include_required_rights_source_metadata() -> None:
    asset_columns = set(Asset.__table__.c)

    assert {"rights_status", "source_label", "source_url", "rights_confirmed_at"} <= {
        column.name for column in asset_columns
    }


def test_phase_10_mask_artifacts_have_distinct_kind() -> None:
    assert enums.ArtifactKind.MASK.value == "mask"


def test_phase_10_edit_intent_schema_round_trips_to_json() -> None:
    from caragent_core.editing import EditIntent

    intent = EditIntent.model_validate(
        {
            "mask": {
                "artifact_id": "11111111-1111-1111-1111-111111111111",
                "content_type": "image/png",
                "height": 768,
                "width": 1536,
            },
            "mode": "targeted_edit",
            "parent_version_id": "22222222-2222-2222-2222-222222222222",
            "prompt_delta": {
                "instructions": ["Move door typography upward."],
                "summary": "Move the selected door text layer.",
            },
            "region": {
                "height": 0.2,
                "type": "rectangle",
                "unit": "normalized",
                "width": 0.4,
                "x": 0.2,
                "y": 0.35,
            },
            "route_preference": "deterministic_recomposition",
            "schema_version": 1,
            "target": {
                "id": "door-main",
                "type": "safe_zone",
            },
        },
    )

    assert intent.model_dump(mode="json") == {
        "mask": {
            "artifact_id": "11111111-1111-1111-1111-111111111111",
            "content_type": "image/png",
            "height": 768,
            "width": 1536,
        },
        "mode": "targeted_edit",
        "parent_version_id": "22222222-2222-2222-2222-222222222222",
        "prompt_delta": {
            "instructions": ["Move door typography upward."],
            "summary": "Move the selected door text layer.",
        },
        "region": {
            "height": 0.2,
            "type": "rectangle",
            "unit": "normalized",
            "width": 0.4,
            "x": 0.2,
            "y": 0.35,
        },
        "route_preference": "deterministic_recomposition",
        "schema_version": 1,
        "target": {
            "id": "door-main",
            "type": "safe_zone",
        },
    }


def test_phase_11_reference_roles_and_snapshots_round_trip_to_json() -> None:
    from caragent_core.references import (
        ReferenceAssignment,
        ReferenceRightsSnapshot,
        ReferenceUsageItem,
        ReferenceUsageSnapshot,
    )

    role_values = {role.value for role in enums.ReferenceRole}
    assert role_values == {
        "character",
        "style",
        "vehicle",
        "logo",
        "palette",
        "inspiration",
    }

    asset_id = "11111111-1111-1111-1111-111111111111"
    assignment = ReferenceAssignment.model_validate(
        {
            "asset_id": asset_id,
            "enabled": True,
            "role": "character",
        },
    )
    assert assignment.model_dump(mode="json") == {
        "asset_id": asset_id,
        "enabled": True,
        "role": "character",
        "schema_version": 1,
    }

    rights = ReferenceRightsSnapshot.model_validate(
        {
            "asset_id": asset_id,
            "checksum_sha256": "a" * 64,
            "content_type": "image/png",
            "object_key": "workspaces/ws/assets/reference.png",
            "original_filename": "reference.png",
            "rights_confirmed_at": None,
            "rights_notes": "artist permission recorded",
            "rights_status": "confirmed",
            "source_label": "Artist upload",
            "source_url": "https://example.test/reference",
        },
    )
    item = ReferenceUsageItem.model_validate(
        {
            "asset_id": asset_id,
            "enabled": True,
            "rights": rights.model_dump(mode="json"),
            "role": "character",
        },
    )
    usage = ReferenceUsageSnapshot.model_validate({"items": [item.model_dump(mode="json")]})

    dumped = usage.model_dump(mode="json")
    assert dumped == {
        "items": [
            {
                "asset_id": asset_id,
                "enabled": True,
                "rights": {
                    "asset_id": asset_id,
                    "checksum_sha256": "a" * 64,
                    "content_type": "image/png",
                    "object_key": "workspaces/ws/assets/reference.png",
                    "original_filename": "reference.png",
                    "rights_confirmed_at": None,
                    "rights_notes": "artist permission recorded",
                    "rights_status": "confirmed",
                    "schema_version": 1,
                    "source_label": "Artist upload",
                    "source_url": "https://example.test/reference",
                },
                "role": "character",
                "schema_version": 1,
            },
        ],
        "schema_version": 1,
    }
    assert "binary" not in str(dumped).lower()
