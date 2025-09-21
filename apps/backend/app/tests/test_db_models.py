from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.db.models import Event, EventMetric, EventTag, Incident


def _alembic_config(db_url: str) -> Config:
    project_root = Path(__file__).resolve().parents[2]
    cfg = Config(str(project_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(project_root / "alembic"))
    cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


@pytest.fixture()
def migrated_engine(tmp_path, monkeypatch):
    db_url = f"sqlite+pysqlite:///{tmp_path/'test.db'}"
    cfg = _alembic_config(db_url)
    monkeypatch.setenv("DATABASE_URL", db_url)
    command.upgrade(cfg, "head")
    engine = create_engine(db_url, future=True)
    try:
        yield engine
    finally:
        engine.dispose()
        command.downgrade(cfg, "base")


def test_event_crud_round_trip(migrated_engine):
    SessionLocal = sessionmaker(bind=migrated_engine, expire_on_commit=False, future=True)
    incident_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    with SessionLocal() as session:
        incident = Incident(
            id=incident_id,
            user_id=uuid.uuid4(),
            status="open",
            score=0.72,
            summary="Elevated resting heart rate",
            last_event_at=now,
        )
        event = Event(
            source="fitbit",
            occurred_at=now,
            received_at=now,
            entity_type="user",
            entity_id="user-123",
            type="health_alert",
            title="Resting HR high",
            body="Resting heart rate increased to 80 bpm.",
            severity_raw="medium",
            links=[{"href": "https://example.com", "rel": "source"}],
            extras={"raw_event_id": "evt-1"},
            features={"resting_hr_z": 2.1},
            score=0.72,
            explain={"resting_hr": 0.5},
            incident=incident,
        )
        event.tag_rows = [EventTag(value="health"), EventTag(value="fitbit")]
        event.metrics = [EventMetric(name="resting_hr", value=80.0, unit="bpm")]
        session.add(event)
        session.commit()
        event_id = event.id

    with SessionLocal() as session:
        stored = session.get(Event, event_id)
        assert stored is not None
        assert stored.incident_id == incident_id
        assert {tag.value for tag in stored.tag_rows} == {"health", "fitbit"}
        assert stored.metrics[0].name == "resting_hr"
        stored.score = 0.9
        stored.links = stored.links + [{"href": "https://example.com/details", "rel": "details"}]
        session.commit()

    with SessionLocal() as session:
        stored = session.get(Event, event_id)
        assert stored.score == pytest.approx(0.9)
        assert len(stored.links) == 2
        session.delete(stored)
        session.commit()
        assert session.get(Event, event_id) is None


def test_migration_downgrade_clears_schema(tmp_path, monkeypatch):
    db_url = f"sqlite+pysqlite:///{tmp_path/'downgrade.db'}"
    cfg = _alembic_config(db_url)
    monkeypatch.setenv("DATABASE_URL", db_url)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")

    engine = create_engine(db_url, future=True)
    try:
        tables = inspect(engine).get_table_names()
        assert "events" not in tables
        assert "incidents" not in tables
    finally:
        engine.dispose()
