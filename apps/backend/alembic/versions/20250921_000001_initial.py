from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20250921_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_incidents_user_id", "incidents", ["user_id"], unique=False)

    op.create_table(
        "events",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=128), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("severity_raw", sa.String(length=32), nullable=True),
        sa.Column("links", sa.JSON(), nullable=False),
        sa.Column("extras", sa.JSON(), nullable=False),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("explain", sa.JSON(), nullable=False),
        sa.Column("incident_id", sa.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_events_incident_id", "events", ["incident_id"], unique=False)
    op.create_index("ix_events_source", "events", ["source"], unique=False)
    op.create_index("ix_events_occurred_at", "events", ["occurred_at"], unique=False)
    op.create_index(
        "ix_events_entity_window",
        "events",
        ["entity_type", "entity_id", "occurred_at"],
        unique=False,
    )

    op.create_table(
        "event_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("value", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "value", name="uq_event_tags_value"),
    )
    op.create_index("ix_event_tags_event_id", "event_tags", ["event_id"], unique=False)

    op.create_table(
        "event_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_metrics_event_id", "event_metrics", ["event_id"], unique=False)
    op.create_index("ix_event_metrics_name", "event_metrics", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_event_metrics_name", table_name="event_metrics")
    op.drop_index("ix_event_metrics_event_id", table_name="event_metrics")
    op.drop_table("event_metrics")

    op.drop_index("ix_event_tags_event_id", table_name="event_tags")
    op.drop_table("event_tags")

    op.drop_index("ix_events_entity_window", table_name="events")
    op.drop_index("ix_events_occurred_at", table_name="events")
    op.drop_index("ix_events_source", table_name="events")
    op.drop_index("ix_events_incident_id", table_name="events")
    op.drop_table("events")

    op.drop_index("ix_incidents_user_id", table_name="incidents")
    op.drop_table("incidents")
