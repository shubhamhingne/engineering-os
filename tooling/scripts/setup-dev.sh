#!/usr/bin/env bash
# Responsibility: take a fresh clone to a runnable dev environment in one command.
# Idempotent and tolerant while the project is a skeleton (Day 8).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

bash tooling/scripts/verify-environment.sh || { echo "Fix the toolchain first."; exit 1; }

echo "→ Starting infrastructure (postgres, redis)…"
docker compose up -d || echo "  (docker not running — start it, then re-run)"

echo "→ Installing workspace dependencies…"
command -v pnpm >/dev/null && pnpm install || echo "  (pnpm install skipped — skeleton)"

echo "→ Preparing env files…"
[ -f apps/api/.env ] || { [ -f apps/api/.env.example ] && cp apps/api/.env.example apps/api/.env || true; }

echo "→ Verifying docs…"
python3 tooling/scripts/check-doc-links.py || true

echo "Setup complete (skeleton). Run commands are finalized during implementation."
