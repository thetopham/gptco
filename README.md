# GPTco — Level-5 Autonomous Company

> **Mission:** Build a governed, observable, tool-using AI that can perform the work of an **organization** (Level-5), not just a chatbot—while enforcing **policy gates, evals, and human oversight**.

**What’s in this repo**
- 🧠 **Executive Brain (Orchestrator)** — plans → tasks → tool actions (A0–A5 autonomy).
- 🧩 **Department Pods** — Growth, Sales, Product/Eng, Finance, Legal, Support.
- 🛠️ **Tool Registry** — typed tool manifests + risk metadata.
- 🗂️ **Memory & RAG** — Postgres (+pgvector) + optional Qdrant.
- 🌐 **Operator** — headless browser worker for end-to-end web tasks.
- 🔌 **MCP (Model Context Protocol) Gateway** — **Dockerized** with plug-and-play MCP servers (filesystem, web, GitHub, Postgres, etc.) to unify tools & context.
- 🧪 **EvalOps** — golden tasks + CI gate; raise autonomy only when passing.
- 🛡️ **Governance** — autonomy tiers (A0–A5), redlines, budget guards, kill-switch.

## Architecture

```
Human OKRs/Policies ───────────────────────────────────┐
                                                        v
┌────────────────────────────────────────────────────────────────────────┐
│ Executive Brain (Orchestrator API)                                      │
│ • OKR→Plans→Tasks • Scheduler • Budget/Risk Guards • Autonomy Gates     │
│ • Incident/Kill-switch • MCP Client (tools & context via MCP Gateway)   │
├───────────────────────────────┬─────────────────────────────────────────┤
│ Department Pods               │ Shared Services                         │
│ • Planner→Toolformer→Reviewer │ • Memory: Postgres + pgvector/Qdrant    │
│ • Growth/Sales/ProdEng/…      │ • RAG: unifies docs/code/email/CRM      │
│ • Policy Guard                │ • Tool Registry: YAML manifests         │
│                               │ • Operator: Playwright headless browser │
│                               │ • Observability: traces, cost, audits   │
├───────────────────────────────┴─────────────────────────────────────────┤
│ MCP Gateway (Docker) + Servers (fs, web, github, postgres, …)           │
└────────────────────────────────────────────────────────────────────────┘
```

## Monorepo Layout

```
gptco/
├─ apps/
│  ├─ orchestrator/             # FastAPI service (Executive Brain)
│  ├─ operator/                 # Playwright worker with allow-list
│  └─ pods/
│     ├─ growth/
│     ├─ sales/
│     ├─ product_eng/
│     ├─ finance/
│     ├─ legal/
│     └─ support/
├─ packages/
│  ├─ tool_registry/            # schema + loader + Python SDK
│  ├─ memory/                   # DB models, embeddings, ingestion
│  ├─ rag/                      # retrieval microservice
│  ├─ policy/                   # autonomy gates + redlines
│  └─ observability/            # tracing, cost meter, audit log
├─ mcp/
│  ├─ gateway/                  # Dockerized MCP Gateway
│  └─ servers/                  # .yaml configs for MCP servers (fs, web…)
├─ configs/
│  ├─ env/.env.example
│  ├─ policy/autonomy_tiers.yaml
│  ├─ policy/redlines.yaml
│  ├─ tools/*.yaml
│  └─ rag/sources.yaml
├─ evals/
│  ├─ tasks/
│  ├─ runners/
│  └─ reports/
├─ infra/
│  ├─ docker-compose.yml
│  └─ migrations/
├─ scripts/
│  ├─ bootstrap.sh
│  ├─ ingest_docs.py
│  └─ run_evals.sh
├─ .github/workflows/ci.yml
├─ Makefile
└─ README.md
```

## Autonomy Tiers
- **A0** Read-only (analysis)
- **A1** Draft-only (no external side-effects)
- **A2** Low-risk, reversible actions
- **A3** Medium-risk with rollback plans
- **A4/A5** Org-scale autonomy with strict redlines + two-person rule

## Quickstart (Docker)

```bash
git clone https://github.com/thetopham/gptco
cd gptco
cp configs/env/.env.example .env
docker compose -f infra/docker-compose.yml up --build -d
docker compose exec orchestrator poe migrate
docker compose exec orchestrator python scripts/ingest_docs.py configs/rag/sources.yaml
curl -s http://localhost:8000/healthz
curl -s -X POST http://localhost:8000/plan -H "Content-Type: application/json" -d '{"okr":"Grow qualified demos by 20%","tier":"A1"}'
```

## MCP Gateway & Servers

Compose adds an `mcp-gateway` service that loads servers from `mcp/servers/mcp.config.yaml`.

## Implementation Roadmap

See **Issues/Milestones**: A0→A1 Foundation, A2/A3 Production Agents, A3 Innovator, A4/A5 Org-scale.

## Security & Governance

- Policies in `configs/policy/*`
- Kill-switch `/admin/kill`
- Two-person rule for payments/contracts
- Budget guard per tier and per tool

MIT License.
