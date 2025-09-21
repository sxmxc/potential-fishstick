.PHONY: up down logs build fmt lint test migrate seed

up:
	docker compose -f infra/docker-compose.yml up -d --build

down:
	docker compose -f infra/docker-compose.yml down

logs:
	docker compose -f infra/docker-compose.yml logs -f --tail=200

build:
	docker compose -f infra/docker-compose.yml build

fmt:
	pre-commit run --all-files || true

lint:
	ruff apps/backend/app || true
	npx eslint apps/web/src --ext .ts,.tsx || true

test:
	# Backend tests
	docker compose -f infra/docker-compose.yml run --rm api pytest -q --disable-warnings --maxfail=1 --cov=app --cov-report=term-missing
	# Web tests
	docker compose -f infra/docker-compose.yml run --rm web npm test -- --runInBand --ci

migrate:
	docker compose -f infra/docker-compose.yml exec api alembic upgrade head || true

seed:
	docker compose -f infra/docker-compose.yml exec api python -m app.utils.seed || true
