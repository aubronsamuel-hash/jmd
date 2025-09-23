"""Ensure artist availability slots are unique."""

from __future__ import annotations

from alembic import op


revision = "20240928_02"
down_revision = "20240926_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        op.f("uq_availabilities_artist_id"),
        "availabilities",
        ["artist_id", "start", "end"],
    )


def downgrade() -> None:
    op.drop_constraint(op.f("uq_availabilities_artist_id"), "availabilities", type_="unique")
