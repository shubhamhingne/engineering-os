"""Publishers — they answer *where the files go*, not what they are. Renderers produce an
ArtifactBundle; publishers ship it (ZIP, GitHub, …). Adding GitLab/Bitbucket/S3 later is a new
publisher, not a change to rendering (ADR-0009)."""
import io
import zipfile
from dataclasses import dataclass
from typing import Optional, Protocol

from ..render.renderers import ArtifactBundle


@dataclass
class PublishResult:
    target: str
    url: Optional[str]
    commit_sha: Optional[str]
    size_bytes: int
    artifact_count: int


class ZipPublisher:
    name = "zip"

    def package(self, bundle: ArtifactBundle) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for artifact in bundle.artifacts:
                zf.writestr(artifact.path, artifact.content)
        return buf.getvalue()

    def publish(self, bundle: ArtifactBundle) -> PublishResult:
        data = self.package(bundle)
        return PublishResult("zip", None, None, len(data), len(bundle.artifacts))


class GitHubClient(Protocol):
    """Port for the GitHub API — real adapter or a fake in tests."""

    def create_repo(self, name: str, private: bool) -> dict:
        ...

    def commit_files(self, full_name: str, files: dict, message: str) -> str:
        ...


class FakeGitHubClient:
    """Deterministic GitHub client for tests — records calls, performs no network I/O."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def create_repo(self, name: str, private: bool) -> dict:
        self.calls.append(("create_repo", name, private))
        return {"full_name": f"shubhamhingne/{name}", "html_url": f"https://github.com/shubhamhingne/{name}"}

    def commit_files(self, full_name: str, files: dict, message: str) -> str:
        self.calls.append(("commit_files", full_name, len(files)))
        return "fake0000deadbeef0000cafe0000sha"


class GitHubPublisher:
    name = "github"

    def __init__(self, client: GitHubClient) -> None:
        self._client = client

    def publish(self, repo_name: str, bundle: ArtifactBundle, private: bool = False) -> PublishResult:
        repo = self._client.create_repo(repo_name, private)
        sha = self._client.commit_files(repo["full_name"], bundle.files(), "Initial commit from Engineering OS")
        size = sum(len(a.content.encode("utf-8")) for a in bundle.artifacts)
        return PublishResult("github", repo.get("html_url"), sha, size, len(bundle.artifacts))
