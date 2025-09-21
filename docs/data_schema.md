# Data Schema (CES)

Event (normalized):
- id, source, occurred_at, received_at
- entity {type,id}, type, title, body, tags[]
- metrics[] (name, value, unit?)
- severity_raw
- links[], extras{}
- features{}, score, explain{}
- incident_id

Incidents: id, user_id, status, score, summary, last_event_at.
Baselines: per (user, entity).
Impact Catalog: exposure weights & meta.
Feedback: useful|not_useful|took_action.
