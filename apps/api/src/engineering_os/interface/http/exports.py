"""Export pipeline endpoints — streamed progress, history, download, and GitHub publishing.

Every route is authorized through `get_owned_project`; the publish route additionally resolves a
GitHub credential from the session and builds the client from it — the publisher never sees OAuth
(ADR-0012)."""
import json
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...adapters.db.models import Project, User
from ...modules.export.service import ExportService
from ...modules.publish.publishers import GitHubPublisher
from ...modules.render.diff import DiffEngine
from .deps import get_current_user, get_db, get_github_client, get_owned_project
from .schemas import (
    BuildPlanItemOut,
    BuildPlanOut,
    BundleDiffOut,
    ExportJobOut,
    PublishRequest,
    PublishResultOut,
)

router = APIRouter(prefix="/api/v1")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/projects/{project_id}/export/stream")
def export_stream(
    project: Project = Depends(get_owned_project), db: Session = Depends(get_db)
) -> StreamingResponse:
    service = ExportService(db)

    def event_stream() -> Iterator[str]:
        try:
            for kind, payload in service.run_stream(project.id):
                yield _sse(kind, payload)
        except Exception as exc:  # surface pipeline failures in-band
            yield _sse("error", {"detail": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/projects/{project_id}/build-plan", response_model=BuildPlanOut)
def build_plan(project: Project = Depends(get_owned_project), db: Session = Depends(get_db)) -> BuildPlanOut:
    plan = ExportService(db).plan(project.id)
    return BuildPlanOut(
        items=[BuildPlanItemOut(renderer=i.renderer, build=i.build, reason=i.reason) for i in plan.items]
    )


@router.get("/projects/{project_id}/export/diff", response_model=BundleDiffOut)
def export_diff(project: Project = Depends(get_owned_project), db: Session = Depends(get_db)) -> BundleDiffOut:
    service = ExportService(db)
    bundle, _project, _count = service.build_bundle(project.id)
    diff = DiffEngine().diff(service.previous_files(project.id), bundle)
    return BundleDiffOut(
        added=diff.added,
        changed=diff.changed,
        unchanged=diff.unchanged,
        removed=diff.removed,
        has_changes=diff.has_changes(),
    )


@router.get("/projects/{project_id}/exports", response_model=list[ExportJobOut])
def list_exports(
    project: Project = Depends(get_owned_project), db: Session = Depends(get_db)
) -> list[ExportJobOut]:
    return [
        ExportJobOut(
            id=j.id,
            status=j.status,
            filename=j.filename,
            size_bytes=j.size_bytes,
            artifact_count=j.artifact_count,
            created_at=j.created_at,
        )
        for j in ExportService(db).history(project.id)
    ]


@router.post("/projects/{project_id}/publish/github", response_model=PublishResultOut)
def publish_github(
    body: PublishRequest,
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
    client=Depends(get_github_client),
) -> PublishResultOut:
    if client is None:
        raise HTTPException(status_code=400, detail="no GitHub credential on this session")
    bundle, _project, _count = ExportService(db).build_bundle(project.id)
    result = GitHubPublisher(client).publish(body.repo_name, bundle, body.private)
    return PublishResultOut(
        target=result.target,
        url=result.url,
        commit_sha=result.commit_sha,
        size_bytes=result.size_bytes,
        artifact_count=result.artifact_count,
    )


@router.get("/exports/{job_id}/download")
def download_export(
    job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Response:
    service = ExportService(db)
    job = service.get(job_id)
    # 404 on both "missing" and "not yours" — never reveal another user's export exists.
    if job is None or db.get(Project, job.project_id).owner_id != user.id:
        raise HTTPException(status_code=404, detail="export not found")
    return Response(
        content=job.zip_data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{job.filename}"'},
    )
