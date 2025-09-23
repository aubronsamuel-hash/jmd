"""Initial persistence schema for planning data."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20240926_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "artists",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_artists")),
    )

    op.create_table(
        "availabilities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("artist_id", sa.Uuid(), nullable=False),
        sa.Column("start", sa.DateTime(timezone=False), nullable=False),
        sa.Column("end", sa.DateTime(timezone=False), nullable=False),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artists.id"],
            name=op.f("fk_availabilities_artist_id_artists"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_availabilities")),
    )

    op.create_table(
        "plannings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_plannings")),
    )

    op.create_table(
        "planning_assignments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("planning_id", sa.Uuid(), nullable=False),
        sa.Column("artist_id", sa.Uuid(), nullable=False),
        sa.Column("availability_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artists.id"],
            name=op.f("fk_planning_assignments_artist_id_artists"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["availability_id"],
            ["availabilities.id"],
            name=op.f("fk_planning_assignments_availability_id_availabilities"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["planning_id"],
            ["plannings.id"],
            name=op.f("fk_planning_assignments_planning_id_plannings"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_planning_assignments")),
    )


def downgrade() -> None:
    op.drop_table("planning_assignments")
    op.drop_table("plannings")
    op.drop_table("availabilities")
    op.drop_table("artists")
