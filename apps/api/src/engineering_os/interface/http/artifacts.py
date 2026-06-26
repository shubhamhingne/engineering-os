"""Generic typed-artifact endpoints. One set of routes serves Vision, PRD, and future types —
no per-type duplication (the payoff of the Artifact abstraction, ADR-0004)."""
import json
import time
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...adapters.db.models import ArtifactVersion
from ...modules.artifacts.service import ArtifactService
from ...modules.generation.service import GenerationService
from ...modules.projects.service import NotFoundError, ProjectService
from ...ports.ai_provider import AIProvider
from .deps import get_db, get_provider
from .schemas import ArtifactSave, ArtifactVersionOut, VersionSummaryOut

router = APIRouter(prefix="/api/v1")

SUPPORTED_TYPES = {"vision", "prd"}  # MVP scope; readme/adr arrive in later slices


def _require_type(artifact_type: str) -> None:
    if artifact_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=404, detail=f"unsupported artifact type: {artifact_type}")


def _require_project(db: Session, project_id: str):
    try:
        return ProjectService(db).get(project_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="project not found")


def _out(artifact_type: str, version: ArtifactVersion) -> ArtifactVersionOut:
    return ArtifactVersionOut(
        type=artifact_type,
        version=version.version_no,
        source=version.source,
        content=version.content,
        model=version.model,
        created_at=version.created_at,
    )


@router.post("/projects/{project_id}/artifacts/{artifact_type}", response_model=ArtifactVersionOut, status_code=201)
def generate_artifact(
    project_id: str,
    artifact_type: str,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_provider),
) -> ArtifactVersionOut:
    _require_type(artifact_type)
    project = _require_project(db, project_id)
    artifacts = ArtifactService(db)

    if artifact_type == "vision":
        context = {"idea": project.idea}
    else:  # prd is generated from the project's Vision
        vision = artifacts.current(project_id, "vision")
        if vision is None:
            raise HTTPException(status_code=409, detail="generate the Vision before the PRD")
        context = {"vision": vision.content}

    try:
        result = GenerationService(provider).generate(artifact_type, context)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _out(artifact_type, artifacts.add_version(project_id, artifact_type, result.content, "ai", result.model))


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/projects/{project_id}/artifacts/{artifact_type}/stream")
def stream_artifact(
    project_id: str,
    artifact_type: str,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_provider),
) -> StreamingResponse:
    _require_type(artifact_type)
    project = _require_project(db, project_id)
    artifacts = ArtifactService(db)

    if artifact_type == "vision":
        context = {"idea": project.idea}
    else:
        vision = artifacts.current(project_id, "vision")
        if vision is None:
            raise HTTPException(status_code=409, detail="generate the Vision before the PRD")
        context = {"vision": vision.content}

    generation = GenerationService(provider)

    def event_stream() -> Iterator[str]:
        started = time.perf_counter()
        for stage in ("building_context", "selecting_prompt", "calling_model"):
            yield _sse("stage", {"stage": stage})

        parts: list[str] = []
        try:
            for chunk in generation.stream(artifact_type, context):
                parts.append(chunk)
                yield _sse("token", {"text": chunk})
        except Exception as exc:  # surface provider failures to the client
            yield _sse("error", {"detail": str(exc)})
            return

        content = "".join(parts)
        yield _sse("stage", {"stage": "formatting"})
        version = artifacts.add_version(project_id, artifact_type, content, "ai", generation.last_model)
        yield _sse("stage", {"stage": "saved"})
        yield _sse(
            "done",
            {
                "type": artifact_type,
                "version": version.version_no,
                "source": version.source,
                "model": version.model,
                "tokens_out": len(content.split()),
                "latency_ms": int((time.perf_counter() - started) * 1000),
            },
        )

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/projects/{project_id}/artifacts/{artifact_type}", response_model=ArtifactVersionOut)
def get_artifact(project_id: str, artifact_type: str, db: Session = Depends(get_db)) -> ArtifactVersionOut:
    _require_type(artifact_type)
    _require_project(db, project_id)
    version = ArtifactService(db).current(project_id, artifact_type)
    if version is None:
        raise HTTPException(status_code=404, detail=f"no {artifact_type} yet")
    return _out(artifact_type, version)


@router.put("/projects/{project_id}/artifacts/{artifact_type}", response_model=ArtifactVersionOut)
def save_artifact(
    project_id: str, artifact_type: str, body: ArtifactSave, db: Session = Depends(get_db)
) -> ArtifactVersionOut:
    _require_type(artifact_type)
    _require_project(db, project_id)
    version = ArtifactService(db).add_version(project_id, artifact_type, body.content, "human")
    return _out(artifact_type, version)


@router.get(
    "/projects/{project_id}/artifacts/{artifact_type}/versions",
    response_model=list[VersionSummaryOut],
)
def list_versions(project_id: str, artifact_type: str, db: Session = Depends(get_db)) -> list[VersionSummaryOut]:
    _require_type(artifact_type)
    _require_project(db, project_id)
    return [
        VersionSummaryOut(version=v.version_no, source=v.source, model=v.model, created_at=v.created_at)
        for v in ArtifactService(db).versions(project_id, artifact_type)
    ]
