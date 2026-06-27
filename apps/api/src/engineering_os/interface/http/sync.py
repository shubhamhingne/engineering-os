"""Repository synchronization endpoint — observe how the remote compares to the local bundle.

This is observation, not publishing: it answers "what does the remote look like, and what's pending?"
The reader (carrying the credential) is injected at the boundary; the compiler never sees the token
(ADR-0015)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...adapters.db.models import Project
from ...modules.artifacts.service import ArtifactService
from ...modules.compiler.passes import REPOSITORY_STATE, compile_sync
from .deps import get_db, get_owned_project, get_repository_reader
from .schemas import RepositoryStateOut

router = APIRouter(prefix="/api/v1")


def _sources(db: Session, project_id: str) -> dict:
    artifacts = ArtifactService(db)
    sources: dict = {}
    for t in artifacts.types_present(project_id):
        if t in ("vision", "prd"):
            current = artifacts.current(project_id, t)
            if current is not None:
                sources[t] = current.content
    return sources


@router.get("/projects/{project_id}/repository-state", response_model=RepositoryStateOut)
def repository_state(
    repository: str,
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
    reader=Depends(get_repository_reader),
) -> RepositoryStateOut:
    if reader is None:
        raise HTTPException(status_code=400, detail="no GitHub credential on this session")
    result = compile_sync(project.title, project.idea, _sources(db, project.id), reader, repository)
    state = result.context.get(REPOSITORY_STATE)
    return RepositoryStateOut(
        repository=state.repository,
        default_branch=state.default_branch,
        published_commit=state.published_commit,
        remote_artifact_hashes=state.remote_artifact_hashes,
        sync_status=state.sync_status,
        pending_artifacts=state.pending_artifacts,
        last_sync=state.last_sync,
        remote_fingerprint=state.remote_fingerprint,
        diagnostics=state.diagnostics,
    )
