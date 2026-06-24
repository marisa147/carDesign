from __future__ import annotations

from pathlib import Path

from caragent_core.models import metadata

API_ROOT = Path(__file__).resolve().parents[1]
VERSIONS_DIR = API_ROOT / "alembic" / "versions"


def test_phase_2_initial_migration_exists_and_covers_ledger_tables() -> None:
    migration_files = list(VERSIONS_DIR.glob("*_phase_02_initial_ledger.py"))
    assert len(migration_files) == 1

    migration = migration_files[0].read_text(encoding="utf-8")

    for table_name in [
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
    ]:
        assert f'op.create_table(\n        "{table_name}",' in migration
        assert table_name in metadata.tables


def test_phase_2_initial_migration_contains_key_constraints() -> None:
    [migration_file] = list(VERSIONS_DIR.glob("*_phase_02_initial_ledger.py"))
    migration = migration_file.read_text(encoding="utf-8")

    assert "uq_generation_jobs_workspace_idempotency" in migration
    assert "uq_job_events_job_sequence" in migration
    assert 'UniqueConstraint("object_key")' in migration
    assert "rights_status" in migration
    assert "source_label" in migration
    assert "source_url" in migration

def test_phase_23_dispatch_outbox_migration_exists() -> None:
    migration_files = list(VERSIONS_DIR.glob("*_phase_23_dispatch_outbox.py"))
    assert len(migration_files) == 1

    migration = migration_files[0].read_text(encoding="utf-8")

    assert 'down_revision: str | None = "f2d60f906fc6"' in migration
    assert 'op.add_column(\n        "generation_jobs"' in migration
    assert '"state_version"' in migration
    assert 'op.create_table(\n        "job_dispatch_outbox"' in migration
    assert "uq_job_dispatch_outbox_job_task" in migration
    assert "ix_job_dispatch_outbox_status_created" in migration
    assert "job_dispatch_outbox" in metadata.tables
