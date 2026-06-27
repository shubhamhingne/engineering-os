"""Export module — render then publish. Renderers build an ArtifactBundle (what files exist);
a publisher ships it (where it goes). ExportJob records a ZIP publish; GitHub is another publisher
(ADR-0006, ADR-0009)."""
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
from ..knowledge.service import KnowledgeExtractor
from ..projects.service import NotFoundError
from ..publish.publishers import ZipPublisher
from ..render.planner import BuildPlan, BuildPlanner
from ..render.renderers import ArtifactBundle, RenderContext, RendererRegistry

log = logging.getLogger("eos.export")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "project"


class ExportService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _present(self, project_id: str) -> dict[str, str]:
        artifacts = ArtifactService(self._db)
        present: dict[str, str] = {}
        for t in artifacts.types_present(project_id):
            current = artifacts.current(project_id, t)
            if current is not None:
                present[t] = current.content
        return present

    def plan(self, project_id: str) -> BuildPlan:
        project = self._db.get(Project, project_id)
        if project is None:
            raise NotFoundError(project_id)
        present = self._present(project_id)
        graph = KnowledgeExtractor().extract(project.title, project.idea, present)
        return BuildPlanner().plan(graph, present)

    def build_bundle(self, project_id: str) -> tuple[ArtifactBundle, Project, int]:
        project = self._db.get(Project, project_id)
        if project is None:
            raise NotFoundError(project_id)
        present = self._present(project_id)
        ctx = RenderContext(title=project.title, idea=project.idea, artifacts=present)
        graph = KnowledgeExtractor().extract(project.title, project.idea, present)
        plan = BuildPlanner().plan(graph, present)
        # Only render what the plan says to build (incremental / conditional generation).
        bundle = RendererRegistry().build(ctx, only=plan.to_build())
        return bundle, project, len(present)

    def previous_files(self, project_id: str) -> dict[str, str]:
        """Files from the most recent export — the baseline for a diff."""
        jobs = self.history(project_id)
        if not jobs:
            return {}
        with zipfile.ZipFile(io.BytesIO(jobs[0].zip_data)) as zf:
            return {name: zf.read(name).decode("utf-8") for name in zf.namelist()}

    def run_stream(self, project_id: str) -> Iterator[tuple[str, dict]]:
        yield ("phase", {"phase": "queued"})
        yield ("phase", {"phase": "preparing"})
        started = time.perf_counter()
        bundle, project, source_count = self.build_bundle(project_id)

        yield ("phase", {"phase": "generating"})
        yield ("phase", {"phase": "packaging"})
        data = ZipPublisher().package(bundle)

        yield ("phase", {"phase": "verifying"})
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            assert "README.md" in zf.namelist()

        job = ExportJob(
            project_id=project_id,
            status="completed",
            filename=f"{_slug(project.title)}.zip",
            size_bytes=len(data),
            artifact_count=source_count,
            zip_data=data,
        )
        self._db.add(job)
        self._db.commit()
        self._db.refresh(job)
        log.info(
            "export.completed",
            extra={
                "artifact_count": source_count,
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
