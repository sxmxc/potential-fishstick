# Connectors (MVP)
- rss: poll feeds → CES
- coinbase_ws: realtime ticker → CES (ETH-USD default)
- fitbit_csv: upload export .zip → parse RHR/sleep → CES
- email_imap: poll alert inbox → CES
- prometheus_webhook: POST receiver → CES

All connectors use `ingest/ces.py` helpers and register in `ingest/registry.py`.
