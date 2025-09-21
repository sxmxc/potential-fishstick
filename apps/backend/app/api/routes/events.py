from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import Select

from app.api.schemas import EventCreate, EventResponse, PaginatedEvents
from app.db import Event, EventMetric, EventTag, Incident
from app.db.session import get_session

router = APIRouter()


def _normalize_to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def _apply_event_filters(
    stmt: Select[Any],
    *,
    source: str | None,
    entity_type: str | None,
    entity_id: str | None,
    incident_id: UUID | None,
    occurred_after: datetime | None,
    occurred_before: datetime | None,
    tag: str | None,
) -> Select[Any]:
    for column, value in [
        (Event.source, source),
        (Event.entity_type, entity_type),
        (Event.entity_id, entity_id),
        (Event.incident_id, incident_id),
    ]:
        if value is not None:
            stmt = stmt.where(column == value)
    if occurred_after:
        stmt = stmt.where(Event.occurred_at >= occurred_after)
    if occurred_before:
        stmt = stmt.where(Event.occurred_at <= occurred_before)
    if tag:
        stmt = stmt.join(EventTag, EventTag.event_id == Event.id).where(EventTag.value == tag)
    return stmt

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=EventResponse,
    response_model_exclude_none=True,
)
def create_event(event: EventCreate, session: Session = Depends(get_session)) -> EventResponse:
    deduped_tags = list(dict.fromkeys(event.tags))
    db_event = Event(
        source=event.source,
        occurred_at=event.occurred_at,
        received_at=event.received_at,
        entity_type=event.entity.type,
        entity_id=event.entity.id,
        type=event.type,
        title=event.title,
        body=event.body,
        severity_raw=event.severity_raw,
        links=[link.model_dump(mode="json", exclude_none=True) for link in event.links],
        extras=event.extras,
        features=event.features,
        score=event.score,
        explain=event.explain,
        incident_id=event.incident_id,
    )
    db_event.tag_rows = [EventTag(value=value) for value in deduped_tags]
    db_event.metrics = [
        EventMetric(name=metric.name, value=metric.value, unit=metric.unit)
        for metric in event.metrics
    ]
    session.add(db_event)
    if event.incident_id is not None:
        incident = session.get(Incident, event.incident_id)
        if incident is not None:
            last_event_at = incident.last_event_at
            if last_event_at is None or _normalize_to_utc(event.occurred_at) > _normalize_to_utc(last_event_at):
                incident.last_event_at = event.occurred_at
    session.commit()
    session.refresh(db_event)
    return EventResponse.model_validate(db_event)

@router.get(
    "/",
    response_model=PaginatedEvents,
    response_model_exclude_none=True,
)
def list_events(
    session: Session = Depends(get_session),
    source: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    incident_id: UUID | None = None,
    tag: str | None = None,
    occurred_after: datetime | None = None,
    occurred_before: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedEvents:
    base_stmt = (
        select(Event)
        .options(selectinload(Event.metrics), selectinload(Event.tag_rows))
        .order_by(Event.occurred_at.desc(), Event.id.desc())
    )
    base_stmt = _apply_event_filters(
        base_stmt,
        source=source,
        entity_type=entity_type,
        entity_id=entity_id,
        incident_id=incident_id,
        occurred_after=occurred_after,
        occurred_before=occurred_before,
        tag=tag,
    )
    paginated_stmt = base_stmt.offset(offset).limit(limit)
    events = session.execute(paginated_stmt).unique().scalars().all()
    items = [EventResponse.model_validate(event) for event in events]

    count_stmt = select(func.count(func.distinct(Event.id))).select_from(Event)
    count_stmt = _apply_event_filters(
        count_stmt,
        source=source,
        entity_type=entity_type,
        entity_id=entity_id,
        incident_id=incident_id,
        occurred_after=occurred_after,
        occurred_before=occurred_before,
        tag=tag,
    )
    total = session.execute(count_stmt).scalar_one()

    return PaginatedEvents(items=items, total=total, limit=limit, offset=offset)
