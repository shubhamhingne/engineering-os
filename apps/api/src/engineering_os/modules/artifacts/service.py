"""Artifacts module — typed artifacts with append-only version history."""
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...adapters.db.models import Artifact, ArtifactVersion

log = logging.getLogger("eos.artifacts")


class ArtifactService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _artifact(self, project_id: str, artifact_type: str) -> Optional[Artifact]:
        return self._db.scalar(
            select(Artifact).where(
                Artifact.project_id == project_id, Artifact.type == artifact_type
            )
        )

    def add_version(
        self, project_id: str, artifact_type: str, content: str, source: str, model: Optional[str] = None
    ) -> ArtifactVersion:
        artifact = self._artifact(project_id, artifact_type)
        if artifact is None:
            artifact = Artifact(project_id=project_id, type=artifact_type)
            self._db.add(artifact)
            self._db.flush()
        next_no = max((v.version_no for v in artifact.versions), default=0) + 1
        version = ArtifactVersion(
            artifact_id=artifact.id, version_no=next_no, content=content, source=source, model=model
        )
        self._db.add(version)
        self._db.commit()
        self._db.refresh(version)
        log.info(
            "artifact.version.created",
            extra={"artifact_type": artifact_type, "version_no": next_no, "source": source},
        )
        return version

    def current(self, project_id: str, artifact_type: str) -> Optional[ArtifactVersion]:
        artifact = self._artifact(project_id, artifact_type)
        if artifact is None or not artifact.versions:
            return None
        return max(artifact.versions, key=lambda v: v.version_no)

    def versions(self, project_id: str, artifact_type: str) -> list[ArtifactVersion]:
        artifact = self._artifact(project_id, artifact_type)
        if artifact is None:
            return []
        return sorted(artifact.versions, key=lambda v: v.version_no, reverse=True)

    def types_present(self, project_id: str) -> list[str]:
        rows = self._db.scalars(select(Artifact.type).where(Artifact.project_id == project_id))
        return sorted(rows)
