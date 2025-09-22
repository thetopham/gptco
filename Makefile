.PHONY: up down logs shell migrate evals seed

up:
	docker compose -f infra/docker-compose.yml up --build -d
down:
	docker compose -f infra/docker-compose.yml down
logs:
	docker compose logs -f orchestrator operator mcp-gateway
shell:
	docker compose exec orchestrator bash
migrate:
	docker compose exec orchestrator poe migrate || true
evals:
	docker compose exec orchestrator bash scripts/run_evals.sh || true
seed:
	docker compose exec orchestrator python scripts/ingest_docs.py configs/rag/sources.yaml || true
