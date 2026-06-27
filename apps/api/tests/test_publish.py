"""Publishers ship a bundle (the 'where it goes' layer). ZIP is real; GitHub via a fake client."""
import io
import zipfile

from engineering_os.interface.http.deps import get_github_client
from engineering_os.main import app
from engineering_os.modules.publish.publishers import FakeGitHubClient, GitHubPublisher, ZipPublisher
from engineering_os.modules.render.renderers import RenderContext, RendererRegistry


def _bundle():
    return RendererRegistry().build(RenderContext(title="App", idea="a FastAPI app", artifacts={"vision": "# V\n\n## Vision\nx\n"}))


def test_zip_publisher_packages_bundle():
    data = ZipPublisher().package(_bundle())
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
    assert "README.md" in names and "LICENSE" in names


def test_github_publisher_with_fake_client():
    fake = FakeGitHubClient()
    result = GitHubPublisher(fake).publish("my-repo", _bundle(), private=False)
    assert result.target == "github"
    assert result.url is not None and result.url.endswith("/my-repo")
    assert result.commit_sha and result.artifact_count >= 3
    kinds = [call[0] for call in fake.calls]
    assert "create_repo" in kinds and "commit_files" in kinds


def test_publish_github_endpoint_with_fake(client):
    app.dependency_overrides[get_github_client] = lambda: FakeGitHubClient()
    pid = client.post("/api/v1/projects", json={"title": "T", "idea": "a FastAPI app"}).json()["id"]
    client.post(f"/api/v1/projects/{pid}/artifacts/vision")
    r = client.post(f"/api/v1/projects/{pid}/publish/github", json={"repo_name": "my-repo"})
    assert r.status_code == 200
    data = r.json()
    assert data["target"] == "github" and data["url"].endswith("/my-repo") and data["commit_sha"]


def test_publish_github_no_credential_400(client):
    # No GitHub credential on the session → the client cannot be built → 400 (not a crash).
    app.dependency_overrides[get_github_client] = lambda: None
    pid = client.post("/api/v1/projects", json={"title": "T", "idea": "x"}).json()["id"]
    assert client.post(f"/api/v1/projects/{pid}/publish/github", json={"repo_name": "r"}).status_code == 400
