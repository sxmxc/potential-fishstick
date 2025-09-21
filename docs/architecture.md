# Architecture

Pipeline: Connectors → CES Normalization → Enrichment → Feature Extraction → Scoring → Correlation → Delivery → Feedback → Learning.

- **Connectors**: rss, coinbase_ws, fitbit_csv, email_imap, prometheus_webhook.
- **Storage**: Postgres (OLTP), MinIO (raw payloads), Redis (queues, caches).
- **Workers**: background tasks for feature calc, scoring, correlation, delivery.
- **Delivery**: Web UI (Next.js), Slack DM (optional), email digests.
- **Privacy**: field-level redaction; at-rest encryption via container configs.
