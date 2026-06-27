"""Export module — runs a project through an observable pipeline and produces a packaged ZIP.

Modeled as a job (ExportJob) with streamed phases, mirroring AI generation. The pipeline can grow
(GitHub push, more outputs) without changing the shape — ADR-0006.
"""
import io
import logging
import re
import time
import zipfile
from collections.abc import Iterator
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...adapters.db.models import ExportJob, Project
from ..artifacts.service import ArtifactService
from ..projects.service import NotFoundError

log = logging.getLogger("eos.export")

PHASES = ("queued", "preparing", "generating", "packaging", "verifying")

_MIT = "MIT License\n\nCopyright (c) 2026 Shubham Hingne\n\nPermission is hereby granted, free of charge, ...\n"
_GITIGNORE = "node_modules/\n.venv/\n__pycache__/\n.env\n.DS_Store\ndist/\n.next/\n"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "project"


class ExportService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _readme(self, project: Project, artifacts: dict[str, str]) -> str:
        present = ", ".join(sorted(artifacts)) or "—"
        lines = [
            f"# {project.title}",
            "",
            f"{project.idea}",
            "",
            "## Artifacts",
            present,
            "",
            "## Documents",
        ]
        for t in sorted(artifacts):
            lines.append(f"- [{t.upper()}](docs/{t}.md)")
        lines += ["", "_Exported from Engineering OS._", ""]
        return "\n".join(lines)

    def _package(self, project: Project, artifacts: dict[str, str]) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("README.md", self._readme(project, artifacts))
            zf.writestr("LICENSE", _MIT)
            zf.writestr(".gitignore", _GITIGNORE)
            for artifact_type, content in artifacts.items():
                zf.writestr(f"docs/{artifact_type}.md", content)
        return buf.getvalue()

    def run_stream(self, project_id: str) -> Iterator[tuple[str, dict]]:
        """Yield ('phase', {...}) events, then a final ('done', {...}). Persists the ExportJob."""
        project = self._db.get(Project, project_id)
        if project is None:
            raise NotFoundError(project_id)

        started = time.perf_counter()
        artifacts_svc = ArtifactService(self._db)

        yield ("phase", {"phase": "queued"})
        yield ("phase", {"phase": "preparing"})
        present: dict[str, str] = {}
        for t in artifacts_svc.types_present(project_id):
            current = artifacts_svc.current(project_id, t)
            if current is not None:
                present[t] = current.content

        yield ("phase", {"phase": "generating"})  # README assembled inside _package
        yield ("phase", {"phase": "packaging"})
        data = self._package(project, present)

        yield ("phase", {"phase": "verifying"})
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            assert "README.md" in zf.namelist()

        job = ExportJob(
            project_id=project_id,
            status="completed",
            filename=f"{_slug(project.title)}.zip",
            size_bytes=len(data),
            artifact_count=len(present),
            zip_data=data,
        )
        self._db.add(job)
        self._db.commit()
        self._db.refresh(job)

        log.info(
            "export.completed",
            extra={
                "artifact_count": len(present),
                "size_bytes": len(data),
                "latency_ms": int((time.perf_counter() - started) * 1000),
            },
        )
        yield (
            "done",
            {
                "job_id": job.id,
                "filename": job.filename,
                "size_bytes": job.size_bytes,
                "artifact_count": job.artifact_count,
            },
        )

    def history(self, project_id: str) -> list[ExportJob]:
        return list(
            self._db.scalars(
                select(ExportJob).where(ExportJob.project_id == project_id).order_by(ExportJob.created_at.desc())
            )
        )

    def get(self, job_id: str) -> Optional[ExportJob]:
        return self._db.get(ExportJob, job_id)
