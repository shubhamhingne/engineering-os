"""Projects module — the aggregate root. Artifacts are managed via ArtifactService."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...adapters.db.models import Project


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
