"""Audit trail tables for compliance workflows."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20241002_03"
down_revision = "20240928_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("actor_type", sa.String(length=64), nullable=True),
        sa.Column("actor_id", sa.String(length=128), nullable=True),
        sa.Column("target_type", sa.String(length=64), nullable=True),
        sa.Column("target_id", sa.String(length=128), nullable=True),
        sa.Column("payload_version", sa.Integer(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("signature", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archive_reference", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )

    op.create_table(
        "audit_retention_policies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("archive_after_days", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("retention_days > 0", name=op.f("ck_audit_retention_positive")),
        sa.CheckConstraint(
            "archive_after_days > 0", name=op.f("ck_audit_retention_archive_positive")
        ),
        sa.CheckConstraint(
            "retention_days >= archive_after_days",
            name=op.f("ck_audit_retention_windows"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_retention_policies")),
        sa.UniqueConstraint(
            "organization_id", name=op.f("uq_audit_retention_policies_organization_id")
        ),
    )

    op.create_table(
        "audit_retention_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("purged_count", sa.Integer(), nullable=False),
        sa.Column("archived_count", sa.Integer(), nullable=False),
        sa.Column("anonymized_count", sa.Integer(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_retention_events")),
    )

    op.create_table(
        "rgpd_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("request_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("requester", sa.String(length=128), nullable=False),
        sa.Column("subject_reference", sa.String(length=128), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processor", sa.String(length=128), nullable=True),
        sa.Column("resolution_notes", sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rgpd_requests")),
    )

    op.create_table(
        "rgpd_request_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("request_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["rgpd_requests.id"],
            name=op.f("fk_rgpd_request_history_request_id_rgpd_requests"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rgpd_request_history")),
    )


def downgrade() -> None:
    op.drop_table("rgpd_request_history")
    op.drop_table("rgpd_requests")
    op.drop_table("audit_retention_events")
    op.drop_table("audit_retention_policies")
    op.drop_table("audit_logs")
