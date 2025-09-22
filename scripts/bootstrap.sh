#!/usr/bin/env bash
set -euo pipefail
poetry install || pip install -r requirements.txt || true
alembic upgrade head || true
python scripts/ingest_docs.py configs/rag/sources.yaml || true
