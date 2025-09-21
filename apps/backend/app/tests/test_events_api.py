import uuid
from datetime import datetime, timedelta, timezone

from app.db import Event, Incident


def test_events_and_incidents_flow(api_client) -> None:
    client, session_factory = api_client
    def build_payload(
        *,
        source: str,
        occurred_at: datetime,
        entity_type: str,
        entity_id: str,
        event_type: str,
        title: str,
        tags: list[str],
        links: list[dict] | None = None,
        metrics: list[dict] | None = None,
    ) -> dict:
        return {
            "source": source,
            "occurred_at": occurred_at.isoformat(),
            "received_at": (occurred_at + timedelta(seconds=5)).isoformat(),
            "entity": {"type": entity_type, "id": entity_id},
            "type": event_type,
            "title": title,
            "tags": tags,
            "links": links or [],
            "metrics": metrics or [],
        }

    def post_event(payload: dict) -> dict:
        response = client.post("/events/", json=payload)
        assert response.status_code == 201
        return response.json()

    first_time = datetime(2025, 9, 20, 12, tzinfo=timezone.utc)
    second_time = first_time + timedelta(minutes=2)
    first_event, _ = tuple(
        post_event(payload)
        for payload in (
            build_payload(
                source="fitbit",
                occurred_at=first_time,
                entity_type="user",
                entity_id="user-123",
                event_type="health_alert",
                title="Resting HR high",
                tags=["health", "fitbit"],
            ),
            build_payload(
                source="alpaca",
                occurred_at=second_time,
                entity_type="portfolio",
                entity_id="acct-9",
                event_type="finance_alert",
                title="Portfolio drawdown",
                tags=["finance", "portfolio"],
            ),
        )
    )
    assert first_event["entity"]["id"] == "user-123"

    for params, expected_total, expected_entity in (
        ({"limit": 1}, 2, "acct-9"),
        ({"source": "fitbit"}, 1, "user-123"),
        ({"tag": "portfolio"}, 1, "acct-9"),
    ):
        payload = client.get("/events/", params=params).json()
        assert payload["total"] == expected_total
        assert payload["items"][0]["entity"]["id"] == expected_entity

    assert client.post("/events/", json={"source": "fitbit"}).status_code == 422

    now = datetime(2025, 9, 20, 13, tzinfo=timezone.utc)
    open_incident_id = uuid.uuid4()
    user_id = uuid.uuid4()
    with session_factory() as session:
        session.add_all(
            [
                Incident(id=open_incident_id, user_id=user_id, status="open", last_event_at=now),
                Incident(
                    id=uuid.uuid4(),
                    user_id=uuid.uuid4(),
                    status="closed",
                    last_event_at=now - timedelta(hours=1),
                ),
            ]
        )
        session.commit()

    follow_up = build_payload(
        source="fitbit",
        occurred_at=now,
        entity_type="user",
        entity_id="user-123",
        event_type="health_alert",
        title="Follow-up",
        tags=["health"],
    )
    follow_up["incident_id"] = str(open_incident_id)
    post_event(follow_up)

    for params, total, incident, count in (
        ({"limit": 1}, 2, None, None),
        ({"status": "open"}, 1, str(open_incident_id), 1),
        ({"user_id": str(user_id)}, 1, str(open_incident_id), None),
    ):
        data = client.get("/incidents/", params=params).json()
        assert data["total"] == total
        if incident:
            assert data["items"][0]["id"] == incident
        if count is not None:
            assert data["items"][0]["event_count"] == count


def test_create_event_with_links_and_metrics(api_client) -> None:
    client, session_factory = api_client
    occurred_at = datetime(2025, 9, 22, 15, tzinfo=timezone.utc)
    payload = {
        "source": "fitbit",
        "occurred_at": occurred_at.isoformat(),
        "received_at": (occurred_at + timedelta(seconds=2)).isoformat(),
        "entity": {"type": "user", "id": "user-123"},
        "type": "health_alert",
        "title": "High resting HR",
        "tags": ["health"],
        "links": [
            {"href": "https://example.com/event", "text": "View"},
            {"href": "https://example.com/details", "rel": "details", "text": None},
        ],
        "metrics": [
            {"name": "resting_hr", "value": 80.0, "unit": "bpm"},
            {"name": "stress_score", "value": 0.75},
        ],
    }

    response = client.post("/events/", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["links"] == [
        {"href": "https://example.com/event", "text": "View"},
        {"href": "https://example.com/details", "rel": "details"},
    ]
    assert data["metrics"] == [
        {"name": "resting_hr", "value": 80.0, "unit": "bpm"},
        {"name": "stress_score", "value": 0.75},
    ]

    with session_factory() as session:
        stored = session.get(Event, uuid.UUID(data["id"]))
        assert stored is not None
        assert stored.links == [
            {"href": "https://example.com/event", "text": "View"},
            {"href": "https://example.com/details", "rel": "details"},
        ]
        stored_metrics = {
            (metric.name, metric.value, metric.unit)
            for metric in stored.metrics
        }
        assert stored_metrics == {
            ("resting_hr", 80.0, "bpm"),
            ("stress_score", 0.75, None),
        }
