"""Compiler-output endpoints — the ExplanationGraph (the differentiator) and the CompilationReport
(the build log). Both run the same validated pipeline; one returns a semantic artifact, the other
the metadata about producing it."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...adapters.db.models import Project
from ...modules.artifacts.service import ArtifactService
from ...modules.compiler.passes import compile_project, run_explain_pipeline
from .deps import get_db, get_owned_project
from .schemas import CompilationReportOut, ExplanationOut, PassResultOut

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


@router.get("/projects/{project_id}/explanations", response_model=list[ExplanationOut])
def explanations(
    project: Project = Depends(get_owned_project), db: Session = Depends(get_db)
) -> list[ExplanationOut]:
    graph = run_explain_pipeline(project.title, project.idea, _sources(db, project.id))
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


@router.get("/projects/{project_id}/compilation-report", response_model=CompilationReportOut)
def compilation_report(
    project: Project = Depends(get_owned_project), db: Session = Depends(get_db)
) -> CompilationReportOut:
    report = compile_project(project.title, project.idea, _sources(db, project.id)).report
    return CompilationReportOut(
        compiler_version=report.compiler_version,
        fingerprint=report.fingerprint,
        schema_versions=report.schema_versions,
        passes_executed=[
            PassResultOut(
                pass_id=p.pass_id,
                duration_ms=p.duration_ms,
                cache_hit=p.cache_hit,
                inputs=p.inputs,
                outputs=p.outputs,
                input_hash=p.input_hash,
                output_hash=p.output_hash,
                invalidation_reason=p.invalidation_reason,
                warnings=p.warnings,
                errors=p.errors,
            )
            for p in report.passes_executed
        ],
        artifacts_generated=report.artifacts_generated,
        artifacts_reused=report.artifacts_reused,
        cache_hits=report.cache_hits,
        warnings=report.warnings,
        duration_ms=report.duration_ms,
        commit_sha=report.commit_sha,
    )
