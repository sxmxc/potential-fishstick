from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_SQLITE_URL = "sqlite+pysqlite:///./signalos.db"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, future=True)
_engine: Engine | None = None
_engine_url: str | None = None


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    host = os.getenv("POSTGRES_HOST")
    if host:
        user = os.getenv("POSTGRES_USER", "signal")
        password = os.getenv("POSTGRES_PASSWORD", "signal")
        database = os.getenv("POSTGRES_DB", "signalos")
        return f"postgresql+psycopg://{user}:{password}@{host}/{database}"
    return DEFAULT_SQLITE_URL


def get_engine(url: str | None = None) -> Engine:
    global _engine, _engine_url
    resolved = url or get_database_url()
    normalized = str(make_url(resolved))
    if _engine is None or _engine_url != normalized:
        _engine = create_engine(normalized, echo=False, future=True, pool_pre_ping=True)
        SessionLocal.configure(bind=_engine)
        _engine_url = str(_engine.url)
    return _engine


def get_session() -> Generator[Session, None, None]:
    get_engine()
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
