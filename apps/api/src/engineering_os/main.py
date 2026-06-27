"""Application composition root."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import init_db
from .interface.http.artifacts import router as artifacts_router
from .interface.http.exports import router as exports_router
from .interface.http.projects import router as projects_router
from .observability import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    init_db()

    app = FastAPI(title="Engineering OS API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(projects_router)
    app.include_router(artifacts_router)
    app.include_router(exports_router)
    return app


app = create_app()
