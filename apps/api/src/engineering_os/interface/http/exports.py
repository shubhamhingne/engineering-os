"""Export pipeline endpoints — streamed progress, history, and download."""
import json
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...modules.export.service import ExportService
from ...modules.projects.service import NotFoundError, ProjectService
from ...modules.publish.publishers import GitHubPublisher
from .deps import get_db, get_github_client
from .schemas import ExportJobOut, PublishRequest, PublishResultOut

router = APIRouter(prefix="/api/v1")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _require_project(db: Session, project_id: str):
    try:
        return ProjectService(db).get(project_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="project not found")


@router.post("/projects/{project_id}/export/stream")
def export_stream(project_id: str, db: Session = Depends(get_db)) -> StreamingResponse:
    _require_project(db, project_id)
    service = ExportService(db)

    def event_stream() -> Iterator[str]:
        try:
            for kind, payload in service.run_stream(project_id):
                yield _sse(kind, payload)
        except Exception as exc:  # surface pipeline failures in-band
            yield _sse("error", {"detail": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/projects/{project_id}/exports", response_model=list[ExportJobOut])
def list_exports(project_id: str, db: Session = Depends(get_db)) -> list[ExportJobOut]:
    _require_project(db, project_id)
    return [
        ExportJobOut(
            id=j.id,
            status=j.status,
            filename=j.filename,
            size_bytes=j.size_bytes,
            artifact_count=j.artifact_count,
            created_at=j.created_at,
        )
        for j in ExportService(db).history(project_id)
    ]


@router.post("/projects/{project_id}/publish/github", response_model=PublishResultOut)
def publish_github(
    project_id: str,
    body: PublishRequest,
    db: Session = Depends(get_db),
    client=Depends(get_github_client),
) -> PublishResultOut:
    _require_project(db, project_id)
    if client is None:
        raise HTTPException(status_code=400, detail="GitHub is not configured (token required)")
    bundle, _project, _count = ExportService(db).build_bundle(project_id)
    result = GitHubPublisher(client).publish(body.repo_name, bundle, body.private)
    return PublishResultOut(
        target=result.target,
        url=result.url,
        commit_sha=result.commit_sha,
        size_bytes=result.size_bytes,
        artifact_count=result.artifact_count,
    )


@router.get("/exports/{job_id}/download")
def download_export(job_id: str, db: Session = Depends(get_db)) -> Response:
    job = ExportService(db).get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="export not found")
    return Response(
        content=job.zip_data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{job.filename}"'},
    )
