# syntax=docker/dockerfile:1
# Production image for the Engineering OS API.
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install the package and its runtime dependencies.
COPY pyproject.toml ./
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini docker-entrypoint.sh ./
RUN pip install --no-cache-dir . \
    && chmod +x docker-entrypoint.sh \
    && useradd --uid 10001 --no-create-home appuser

USER appuser
EXPOSE 8000

# Liveness for the container runtime (distinct from the app's readiness probe).
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=5 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health/live').status==200 else 1)"

# Entrypoint runs migrations, then serves.
CMD ["./docker-entrypoint.sh"]
