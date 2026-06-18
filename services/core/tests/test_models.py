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
