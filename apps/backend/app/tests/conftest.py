from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.db.session import get_session
from app.main import app


@pytest.fixture()
def api_client(tmp_path) -> Iterator[tuple[TestClient, sessionmaker[Session]]]:
    db_path = tmp_path / "api.sqlite"
    engine = create_engine(
        f"sqlite+pysqlite:///{db_path}", future=True, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory: sessionmaker[Session] = sessionmaker(bind=engine, expire_on_commit=False, future=True)

    def override_get_session() -> Iterator[Session]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(app) as client:
            yield client, factory
    finally:
        app.dependency_overrides.pop(get_session, None)
        engine.dispose()
