"""Project CRUD endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...adapters.db.models import Project, User
from ...modules.artifacts.service import ArtifactService
from ...modules.projects.service import ProjectService
from .deps import get_current_user, get_db, get_owned_project
from .schemas import ProjectCreate, ProjectOut

router = APIRouter(prefix="/api/v1")


def _to_out(db: Session, project: Project) -> ProjectOut:
    return ProjectOut(
        id=project.id,
        title=project.title,
        idea=project.idea,
        artifact_types=ArtifactService(db).types_present(project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post("/projects", response_model=ProjectOut, status_code=201)
def create_project(
    body: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> ProjectOut:
    return _to_out(db, ProjectService(db).create(body.title, body.idea, owner_id=user.id))


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ProjectOut]:
    return [_to_out(db, p) for p in ProjectService(db).list(owner_id=user.id)]


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project: Project = Depends(get_owned_project), db: Session = Depends(get_db)) -> ProjectOut:
    return _to_out(db, project)
