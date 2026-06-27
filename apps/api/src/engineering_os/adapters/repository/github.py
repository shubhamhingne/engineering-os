"""Repository readers: a real GitHub adapter + a deterministic fake — the same fake/real split as
every other port. The reader only *reads*; it never writes (ADR-0015)."""
import hashlib
from typing import Optional

from ...ports.repository import RemoteSnapshot

_API = "https://api.github.com"


def _content_hash(content: bytes) -> str:
    """Our content-hash scheme (sha256[:12]), recomputed from remote bytes so local and remote
    hashes are directly comparable — GitHub's git blob SHA uses a different formula."""
    return hashlib.sha256(content).hexdigest()[:12]


class GitHubRepositoryReader:
    """Reads a repo's default branch, head commit, and per-file content hashes. Used only when a
    token is configured; the deterministic fake covers tests."""

    def __init__(self, token: str) -> None:
        self._token = token

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._token}", "Accept": "application/vnd.github+json"}

    def read_state(self, repository: str) -> Optional[RemoteSnapshot]:
        import httpx

        with httpx.Client(headers=self._headers(), timeout=10.0) as client:
            repo = client.get(f"{_API}/repos/{repository}")
            if repo.status_code == 404:
                return None
            repo.raise_for_status()
            default_branch = repo.json().get("default_branch", "main")

            head = client.get(f"{_API}/repos/{repository}/commits/{default_branch}")
            head.raise_for_status()
            head_sha = head.json()["sha"]

            tree = client.get(
                f"{_API}/repos/{repository}/git/trees/{head_sha}", params={"recursive": "1"}
            )
            tree.raise_for_status()
            hashes: dict = {}
            for entry in tree.json().get("tree", []):
                if entry.get("type") != "blob":
                    continue
                blob = client.get(f"{_API}/repos/{repository}/git/blobs/{entry['sha']}")
                blob.raise_for_status()
                import base64

                content = base64.b64decode(blob.json()["content"])
                hashes[entry["path"]] = _content_hash(content)

        return RemoteSnapshot(
            repository=repository,
            default_branch=default_branch,
            head_commit=head_sha,
            artifact_hashes=hashes,
        )


class FakeRepositoryReader:
    """Deterministic reader for tests/dev. Construct with a snapshot to simulate a published repo,
    or with None to simulate one that doesn't exist yet."""

    def __init__(self, snapshot: Optional[RemoteSnapshot] = None) -> None:
        self._snapshot = snapshot
        self.calls: list = []

    def read_state(self, repository: str) -> Optional[RemoteSnapshot]:
        self.calls.append(repository)
        return self._snapshot
