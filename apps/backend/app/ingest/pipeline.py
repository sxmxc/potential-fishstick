from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.schemas import EventCreate
from app.db import Event as EventModel, Incident
from app.services.correlate import should_merge
from app.services.features import feature_vector
from app.services.scoring import score


@dataclass
class PipelineResult:
    """Outcome of running the inline enrichment pipeline for an event."""

    features: dict[str, float]
    score: float
    explain: dict[str, Any]
    incident_id: UUID | None


def process_event(event: EventCreate, session: Session) -> PipelineResult:
    """Run feature extraction, scoring, and correlation for an incoming event."""

    metrics = _metrics_dict(event)
    context = _build_context(event)
    feature_values = feature_vector({"type": event.type, "metrics": metrics}, context)
    score_value = score(feature_values)
    explanation = _explain_score(feature_values, score_value)
    incident_id = event.incident_id or _correlate(event, score_value, session)
    return PipelineResult(
        features=feature_values,
        score=score_value,
        explain=explanation,
        incident_id=incident_id,
    )


def _metrics_dict(event: EventCreate) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for metric in event.metrics:
        try:
            metrics[metric.name] = float(metric.value)
        except (TypeError, ValueError):  # pragma: no cover - validated upstream
            continue
    return metrics


def _build_context(event: EventCreate) -> dict[str, Any]:
    extras = event.extras or {}
    context: dict[str, Any] = {}

    nested = extras.get("context")
    if isinstance(nested, dict):
        context.update(nested)

    context.setdefault("portfolio_exposure", _as_float(extras.get("portfolio_exposure"), 1.0))
    context.setdefault("market_open", _as_bool(extras.get("market_open"), True))
    context.setdefault("personal_relevance", _as_float(extras.get("personal_relevance"), 0.5))
    return context


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value in {"true", "True", "1", 1}:
        return True
    if value in {"false", "False", "0", 0}:
        return False
    return default


def _explain_score(features: dict[str, float], score_value: float) -> dict[str, Any]:
    impact = max(
        features.get("impact_finance", 0.0),
        features.get("impact_health", 0.0),
        features.get("impact_news", 0.0),
    )
    factors = {
        "impact": impact,
        "actionability": features.get("actionability", 0.5),
        "urgency": features.get("urgency", 0.2),
        "personal_relevance": features.get("personal_relevance", 0.5),
    }
    weights = {
        "impact": 0.4,
        "actionability": 0.25,
        "urgency": 0.2,
        "personal_relevance": 0.15,
    }
    contributions = {name: round(value * weights[name], 6) for name, value in factors.items()}
    top_factor = max(contributions.items(), key=lambda item: item[1])[0] if contributions else None
    return {
        "contributions": contributions,
        "top_factor": top_factor,
        "score": round(score_value, 6),
    }


def _correlate(event: EventCreate, score_value: float, session: Session) -> UUID | None:
    lookback_start = event.occurred_at - timedelta(minutes=15)
    new_view = _event_view(event)
    stmt = (
        select(EventModel)
        .options(selectinload(EventModel.tag_rows))
        .where(EventModel.occurred_at >= lookback_start)
        .where(EventModel.occurred_at <= event.occurred_at)
        .order_by(EventModel.occurred_at.desc())
        .limit(50)
    )
    candidates = session.execute(stmt).unique().scalars().all()
    for candidate in candidates:
        candidate_view = _event_view(candidate)
        if should_merge(candidate_view, new_view):
            if candidate.incident_id is not None:
                incident = session.get(Incident, candidate.incident_id)
                if incident is None or incident.status != "open":
                    continue
                _update_incident(incident, score_value, event.occurred_at)
                return incident.id
            incident = Incident(status="open")
            session.add(incident)
            session.flush()
            candidate.incident_id = incident.id
            _update_incident(incident, candidate.score, candidate.occurred_at)
            _update_incident(incident, score_value, event.occurred_at)
            return incident.id
    return None


def _event_view(event: EventCreate | EventModel) -> dict[str, Any]:
    if isinstance(event, EventCreate):
        occurred_at = event.occurred_at
        tags = event.tags
        entity_id = event.entity.id
    else:
        occurred_at = event.occurred_at
        tags = [tag.value for tag in event.tag_rows]
        entity_id = event.entity_id
    occurred_ms = int(occurred_at.timestamp() * 1000)
    return {"entity_id": entity_id, "occurred_at": occurred_ms, "tags": tags}


def _update_incident(incident: Incident, score_value: float | None, occurred_at: datetime) -> None:
    if score_value is not None:
        if incident.score is None or score_value > incident.score:
            incident.score = score_value
    normalized_occurred = _to_utc(occurred_at)
    last_event = incident.last_event_at
    if last_event is None or normalized_occurred > _to_utc(last_event):
        incident.last_event_at = normalized_occurred


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
