from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.schemas import IncidentResponse, PaginatedIncidents
from app.db import Event, Incident
from app.db.session import get_session

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedIncidents,
    response_model_exclude_none=True,
)
def list_incidents(
    session: Session = Depends(get_session),
    status: str | None = None,
    user_id: UUID | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedIncidents:
    filters: list[Any] = []
    if status is not None:
        filters.append(Incident.status == status)
    if user_id is not None:
        filters.append(Incident.user_id == user_id)

    stmt = (
        select(Incident, func.count(Event.id).label("event_count"))
        .outerjoin(Event, Incident.id == Event.incident_id)
        .group_by(Incident.id)
        .order_by(Incident.last_event_at.desc().nullslast(), Incident.id)
    )
    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.offset(offset).limit(limit)

    rows = session.execute(stmt).all()
    items = [
        IncidentResponse(
            id=incident.id,
            user_id=incident.user_id,
            status=incident.status,
            score=incident.score,
            summary=incident.summary,
            last_event_at=incident.last_event_at,
            event_count=event_count,
        )
        for incident, event_count in rows
    ]

    count_stmt = select(func.count(Incident.id))
    if filters:
        count_stmt = count_stmt.where(*filters)
    total = session.execute(count_stmt).scalar_one()

    return PaginatedIncidents(items=items, total=total, limit=limit, offset=offset)
