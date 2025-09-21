# API (MVP)

- GET /health
- GET /events
  - Query params: `source`, `entity_type`, `entity_id`, `incident_id`, `tag`, `occurred_after`, `occurred_before`, `limit`, `offset` (temporal filters expect ISO 8601 datetimes).
  - Returns `total`, `limit`, `offset`, and `items` ordered by newest `occurred_at`.
- POST /events (ingest)
- GET /incidents
  - Query params: `status`, `user_id`, `limit`, `offset`.
  - Each item includes `event_count` and `last_event_at`.
- POST /score (debug)
- POST /connectors/rss/pull (demo)

OpenAPI at /docs (FastAPI).
