# signal-os — Universal Noise→Signal Filter (Starter Repo)

Self-hostable, fully containerized. Ingest multiple streams, normalize via CES, score signals, correlate incidents, and deliver a ranked feed.

## Quickstart
```bash
make up        # build + start all services
make logs      # tail logs
make test      # run backend + web tests in containers
```
Open http://localhost:8080 (nginx → web & api).

## Tests
- **Backend**: pytest + pytest-cov; FastAPI TestClient; unit tests for CES, scoring, correlation, and health.
- **Web**: Jest + React Testing Library; example component test.
Run all: `make test`.

## No Cloud Required
- docker-compose brings up Postgres, Redis, MinIO, API, Web, Nginx — all local.
- Future-ready for Kubernetes with manifests under `infra/k8s` (add later).

## Docs
See `docs/` for architecture, schemas, scoring, and more.
