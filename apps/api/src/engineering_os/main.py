"""Application composition root."""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import settings
from .db import SessionLocal, init_db
from .interface.http.artifacts import router as artifacts_router
from .interface.http.auth import router as auth_router
from .interface.http.compiler import router as compiler_router
from .interface.http.explain import router as explain_router
from .interface.http.exports import router as exports_router
from .interface.http.projects import router as projects_router
from .interface.http.sync import router as sync_router
from .observability import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    # Dev convenience: create tables directly. In production the schema is owned by Alembic
    # migrations (`alembic upgrade head`), run at deploy time — see BR-04.
    if not settings.is_production:
        init_db()

    app = FastAPI(title="Engineering OS API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
        allow_credentials=True,  # session cookie must ride cross-origin requests from the web app
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    @app.get("/health/live")
    def liveness() -> dict[str, str]:
        """Liveness: the process is up and serving. Used by the orchestrator to decide restarts."""
        return {"status": "ok"}

    @app.get("/health/ready")
    def readiness(response: Response) -> dict[str, str]:
        """Readiness: the app can serve real traffic (its dependencies are reachable). Used to decide
        whether to route requests. Returns 503 until the database answers."""
        try:
            with SessionLocal() as db:
                db.execute(text("SELECT 1"))
            return {"status": "ready"}
        except Exception:
            response.status_code = 503
            return {"status": "not ready", "detail": "database unreachable"}

    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(artifacts_router)
    app.include_router(exports_router)
    app.include_router(explain_router)
    app.include_router(compiler_router)
    app.include_router(sync_router)
    return app


app = create_app()
