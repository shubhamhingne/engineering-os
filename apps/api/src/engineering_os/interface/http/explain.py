"""Explainability endpoint — exposes the ExplanationGraph (the differentiator)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...modules.artifacts.service import ArtifactService
from ...modules.compiler.passes import run_explain_pipeline
from ...modules.projects.service import NotFoundError, ProjectService
from .deps import get_db
from .schemas import ExplanationOut

router = APIRouter(prefix="/api/v1")


@router.get("/projects/{project_id}/explanations", response_model=list[ExplanationOut])
def explanations(project_id: str, db: Session = Depends(get_db)) -> list[ExplanationOut]:
    try:
        project = ProjectService(db).get(project_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="project not found")

    artifacts = ArtifactService(db)
    sources: dict[str, str] = {}
    for t in artifacts.types_present(project_id):
        if t in ("vision", "prd"):
            current = artifacts.current(project_id, t)
            if current is not None:
                sources[t] = current.content

    graph = run_explain_pipeline(project.title, project.idea, sources)
    return [
        ExplanationOut(
            entity_id=e.entity_id,
            type=e.type,
            label=e.label,
            summary=e.summary,
            evidence=e.evidence,
            sources=e.sources,
            appears_in=e.appears_in,
            related_decisions=e.related_decisions,
            confidence=e.confidence,
        )
        for e in graph.explanations
    ]
