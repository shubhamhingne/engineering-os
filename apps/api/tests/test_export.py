"""Export pipeline — service (real ZIP) + API (streamed phases, history, download)."""
import io
import zipfile

from engineering_os.modules.artifacts.service import ArtifactService
from engineering_os.modules.export.service import ExportService
from engineering_os.modules.projects.service import ProjectService


def test_export_service_packages_a_valid_zip(db):
    project = ProjectService(db).create("My Tool", "an idea worth building")
    ArtifactService(db).add_version(project.id, "vision", "# Vision\n\nhello", "ai")

    events = list(ExportService(db).run_stream(project.id))
    kinds = [k for k, _ in events]
    assert "phase" in kinds and kinds[-1] == "done"

    job_id = events[-1][1]["job_id"]
    job = ExportService(db).get(job_id)
    assert job is not None and job.status == "completed" and job.size_bytes > 0
    with zipfile.ZipFile(io.BytesIO(job.zip_data)) as zf:
        names = zf.namelist()
    assert "README.md" in names and "docs/vision.md" in names and "LICENSE" in names


def test_export_stream_history_and_download(client):
    project_id = client.post("/api/v1/projects", json={"title": "T", "idea": "an idea"}).json()["id"]
    client.post(f"/api/v1/projects/{project_id}/artifacts/vision")

    with client.stream("POST", f"/api/v1/projects/{project_id}/export/stream") as r:
        assert r.status_code == 200
        body = "".join(r.iter_text())
    assert "event: phase" in body and "event: done" in body

    history = client.get(f"/api/v1/projects/{project_id}/exports").json()
    assert len(history) == 1 and history[0]["artifact_count"] == 1
    job_id = history[0]["id"]

    download = client.get(f"/api/v1/exports/{job_id}/download")
    assert download.status_code == 200 and download.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(download.content)) as zf:
        assert "README.md" in zf.namelist()


def test_export_missing_project_404(client):
    assert client.post("/api/v1/projects/none/export/stream").status_code == 404
