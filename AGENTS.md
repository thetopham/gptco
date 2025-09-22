# Repository Guidelines

## Project Structure & Module Organization
Core services live in `apps/`: `apps/orchestrator` runs the FastAPI autonomy brain and `apps/operator` hosts the Playwright worker stub. Shared libraries sit under `packages/` (e.g., `packages/tool_registry` for manifest parsing). Configuration and policy assets live in `configs/`, including `.env` templates in `configs/env/` and redlines in `configs/policy/`. Evaluation harnesses and golden tasks are in `evals/`, infrastructure manifests in `infra/`, and helper automation in `scripts/` (bootstrap, ingest, eval runners). Use `archive/` only for historical artifacts that should stay out of runtime code paths.

## Build, Test & Development Commands
Use `make up` for the full Docker stack (`infra/docker-compose.yml`) and `make down` to stop containers. Run `make migrate` after schema changes; it calls `poe migrate` inside the orchestrator. For local smoke tests without Docker, install deps and run `uvicorn apps/orchestrator/main:app --reload`. Refresh seed content with `python scripts/ingest_docs.py configs/rag/sources.yaml`.

## Coding Style & Naming Conventions
Target Python 3.11, 4-space indentation, and module-level type hints (see `apps/orchestrator/main.py`). Group imports as standard lib, third-party, then local modules with blank separators. Prefer `snake_case` for functions and files, `PascalCase` for Pydantic models, and explicit enums over magic strings. YAML configs should stay kebab-case and include inline comments when policy assumptions change. Keep FastAPI route handlers thin—delegate policy, gating, or datastore logic to package modules.

## Testing Guidelines
Pytest is the canonical runner; execute `pytest -q evals/runners/test_evals.py` or simply `make evals`, which wraps the Docker invocation. Name new tests `test_*.py` and colocate them with their feature (mirror package paths or extend `evals/runners/`). When adding evals, update fixtures or golden outputs in `evals/tasks/` and store generated reports in `evals/reports/`. Aim to extend coverage for policy gates, audit logging, and tool registry parsing before raising autonomy tiers.

## Commit & Pull Request Guidelines
Follow Conventional Commit prefixes where possible (`feat:`, `fix:`, `chore:`)—recent history already uses `chore:` entries. Keep commits scoped to a single logical change and run `pytest`/`make evals` before pushing. PRs should summarize impact, link relevant issues or OKRs, and call out policy or config changes explicitly. Attach screenshots or trace excerpts when touching operator automation so reviewers can verify headless flows.

## Security & Policy Notes
Never commit real secrets; replicate environment changes in `.env.example` and document them in the PR. Any adjustment to `configs/policy/*` requires a short rationale plus updated redline tests. Validate external tool manifests under `configs/tools/` with risk metadata before enabling them in higher autonomy tiers.
