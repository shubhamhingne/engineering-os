#!/bin/sh
# Migrate, then serve. Migrations run at deploy time so the schema is always current (BR-04).
set -e

echo "[entrypoint] applying database migrations..."
alembic upgrade head

echo "[entrypoint] starting API on :8000..."
exec uvicorn engineering_os.main:app --host 0.0.0.0 --port 8000
