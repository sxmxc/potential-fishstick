from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_SQLITE_URL = "sqlite+pysqlite:///./signalos.db"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, future=True)
_engine: Engine | None = None


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
    global _engine
    resolved = url or get_database_url()
    if _engine is None or str(_engine.url) != resolved:
        _engine = create_engine(resolved, echo=False, future=True, pool_pre_ping=True)
        SessionLocal.configure(bind=_engine)
    return _engine


def get_session() -> Generator[Session, None, None]:
    get_engine()
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
