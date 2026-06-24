"""phase 23 dispatch outbox

Revision ID: 9c6f1c1a7e3d
Revises: f2d60f906fc6
Create Date: 2026-06-22 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9c6f1c1a7e3d"
down_revision: str | None = "f2d60f906fc6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "generation_jobs",
        sa.Column("state_version", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_table(
        "job_dispatch_outbox",
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("task_name", sa.String(length=160), nullable=False),
        sa.Column("queue_name", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("task_id", sa.String(length=160), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("dispatched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["generation_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id", "task_name", name="uq_job_dispatch_outbox_job_task"),
    )
    op.create_index(
        op.f("ix_job_dispatch_outbox_job_id"),
        "job_dispatch_outbox",
        ["job_id"],
        unique=False,
    )
    op.create_index(
        "ix_job_dispatch_outbox_status_created",
        "job_dispatch_outbox",
        ["status", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_job_dispatch_outbox_status_created", table_name="job_dispatch_outbox")
    op.drop_index(op.f("ix_job_dispatch_outbox_job_id"), table_name="job_dispatch_outbox")
    op.drop_table("job_dispatch_outbox")
    op.drop_column("generation_jobs", "state_version")
