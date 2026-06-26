"""Projects module — the aggregate that owns its Vision artifact."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...adapters.db.models import Project, VisionArtifact


class NotFoundError(Exception):
    """Raised when a project does not exist."""


class ProjectService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, title: str, idea: str) -> Project:
        project = Project(title=title.strip(), idea=idea.strip())
        self._db.add(project)
        self._db.commit()
        self._db.refresh(project)
        return project

    def list(self) -> list[Project]:
        return list(self._db.scalars(select(Project).order_by(Project.updated_at.desc())))

    def get(self, project_id: str) -> Project:
        project = self._db.get(Project, project_id)
        if project is None:
            raise NotFoundError(project_id)
        return project

    def get_vision(self, project_id: str) -> Optional[VisionArtifact]:
        return self.get(project_id).vision

    def set_vision(self, project_id: str, content: str, source: str, model: Optional[str] = None) -> VisionArtifact:
        project = self.get(project_id)
        if project.vision is None:
            project.vision = VisionArtifact(content=content, source=source, version=1, model=model)
        else:
            project.vision.content = content
            project.vision.source = source
            project.vision.version += 1
            if model:
                project.vision.model = model
        self._db.commit()
        self._db.refresh(project.vision)
        return project.vision
