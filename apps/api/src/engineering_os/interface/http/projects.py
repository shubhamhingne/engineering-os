"""Project + Vision endpoints — the Day 9 vertical slice."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...adapters.db.models import Project
from ...modules.generation.service import GenerationService
from ...modules.projects.service import NotFoundError, ProjectService
from ...ports.ai_provider import AIProvider
from .deps import get_db, get_provider
from .schemas import ProjectCreate, ProjectOut, VisionOut, VisionUpdate

router = APIRouter(prefix="/api/v1")


def _to_out(project: Project) -> ProjectOut:
    return ProjectOut(
        id=project.id,
        title=project.title,
        idea=project.idea,
        has_vision=project.vision is not None,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post("/projects", response_model=ProjectOut, status_code=201)
def create_project(body: ProjectCreate, db: Session = Depends(get_db)) -> ProjectOut:
    return _to_out(ProjectService(db).create(body.title, body.idea))


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)) -> list[ProjectOut]:
    return [_to_out(p) for p in ProjectService(db).list()]


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)) -> ProjectOut:
    try:
        return _to_out(ProjectService(db).get(project_id))
    except NotFoundError:
        raise HTTPException(status_code=404, detail="project not found")


@router.post("/projects/{project_id}/vision", response_model=VisionOut, status_code=201)
def generate_vision(
    project_id: str,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_provider),
) -> VisionOut:
    service = ProjectService(db)
    try:
        project = service.get(project_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="project not found")
    try:
        result = GenerationService(provider).generate_vision(project.idea)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return service.set_vision(project_id, result.content, source="ai", model=result.model)


@router.get("/projects/{project_id}/vision", response_model=VisionOut)
def get_vision(project_id: str, db: Session = Depends(get_db)) -> VisionOut:
    try:
        vision = ProjectService(db).get_vision(project_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="project not found")
    if vision is None:
        raise HTTPException(status_code=404, detail="no vision yet")
    return vision


@router.put("/projects/{project_id}/vision", response_model=VisionOut)
def save_vision(project_id: str, body: VisionUpdate, db: Session = Depends(get_db)) -> VisionOut:
    service = ProjectService(db)
    try:
        service.get(project_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="project not found")
    return service.set_vision(project_id, body.content, source="human")
