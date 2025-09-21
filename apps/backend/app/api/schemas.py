"""Pydantic schemas exposed by the public API."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

EVENT_CREATE_EXAMPLE = {
    "source": "fitbit",
    "occurred_at": "2025-09-20T12:00:00Z",
    "received_at": "2025-09-20T12:00:05Z",
    "entity": {"type": "user", "id": "user-123"},
    "type": "health_alert",
    "title": "Resting HR high",
    "tags": ["health", "fitbit"],
}

EVENT_RESPONSE_EXAMPLE = {
    **EVENT_CREATE_EXAMPLE,
    "id": "f3a7e4f9-5d39-4d7b-8d2f-2a7b1d2f9c4a",
    "incident_id": "0b2e4e4e-6c7a-4f94-9f20-8f0b61b9b9a4",
}

INCIDENT_RESPONSE_EXAMPLE = {
    "id": "ccf6d6f4-5f1b-4f23-8b61-ec5d5f4b1d12",
    "status": "open",
    "event_count": 3,
}


class EntityRef(BaseModel):
    type: str
    id: str


class EventCreate(BaseModel):
    source: str
    occurred_at: datetime
    received_at: datetime
    entity: EntityRef
    type: str
    title: str
    body: str | None = None
    severity_raw: str | None = None
    tags: list[str] = Field(default_factory=list)
    metrics: list[dict[str, float | None]] = Field(default_factory=list)
    links: list[dict[str, AnyHttpUrl | str | None]] = Field(default_factory=list)
    extras: dict[str, Any] = Field(default_factory=dict)
    features: dict[str, Any] = Field(default_factory=dict)
    score: float | None = None
    explain: dict[str, Any] = Field(default_factory=dict)
    incident_id: UUID | None = None

    model_config = ConfigDict(json_schema_extra={"example": EVENT_CREATE_EXAMPLE})


class EventResponse(EventCreate):
    id: UUID

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": EVENT_RESPONSE_EXAMPLE},
    )


class IncidentResponse(BaseModel):
    id: UUID
    user_id: UUID | None = None
    status: str
    score: float | None = None
    summary: str | None = None
    last_event_at: datetime | None = None
    event_count: int

    model_config = ConfigDict(json_schema_extra={"example": INCIDENT_RESPONSE_EXAMPLE})


class PaginatedBase(BaseModel):
    total: int
    limit: int
    offset: int


class PaginatedEvents(PaginatedBase):
    items: list[EventResponse]


class PaginatedIncidents(PaginatedBase):
    items: list[IncidentResponse]
