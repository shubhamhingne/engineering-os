"""RepositoryState + RepositorySyncPass (Alpha-0.9, ADR-0015). The compiler gains remote-sync as
*pure addition*: one ContextKey, one pass, one report section, zero edits to existing passes. The
sync pass only observes — it never publishes."""
from engineering_os.adapters.repository.github import FakeRepositoryReader
from engineering_os.interface.http.deps import get_repository_reader
from engineering_os.main import app
from engineering_os.modules.compiler.passes import BUNDLE, REPOSITORY_STATE, RepositorySyncPass, compile_sync
from engineering_os.modules.repository.service import build_repository_state
from engineering_os.ports.repository import RemoteSnapshot

SRC = {"vision": "# V\n\n## Problem\nneeds authentication\n"}


# --- The pure comparison (no network) -------------------------------------------------------------

def test_unpublished_when_remote_absent():
    state = build_repository_state("owner/app", {"README.md": "aaa"}, None)
    assert state.sync_status == "unpublished"
    assert state.pending_artifacts == ["README.md"]
    assert state.published_commit is None


def test_in_sync_when_hashes_match():
    local = {"README.md": "aaa", "LICENSE": "bbb"}
    snap = RemoteSnapshot("owner/app", "main", "c0ffee", dict(local))
    state = build_repository_state("owner/app", local, snap)
    assert state.sync_status == "in_sync"
    assert state.pending_artifacts == []
    assert state.published_commit == "c0ffee"


def test_ahead_when_local_differs():
    local = {"README.md": "NEW", "LICENSE": "bbb"}
    snap = RemoteSnapshot("owner/app", "main", "c0ffee", {"README.md": "old", "LICENSE": "bbb"})
    state = build_repository_state("owner/app", local, snap)
    assert state.sync_status == "ahead"
    assert state.pending_artifacts == ["README.md"]


# --- The pass and pipeline ------------------------------------------------------------------------

def test_sync_pass_is_neither_deterministic_nor_cacheable():
    # The one pass that reads live remote state — the flags finally diverge from the extraction passes.
    d = RepositorySyncPass.descriptor
    assert d.deterministic is False and d.cacheable is False
    assert d.consumes == (BUNDLE,) and d.produces == (REPOSITORY_STATE,)


def test_compile_sync_produces_state_and_enriches_report():
    result = compile_sync("App", "a FastAPI app", SRC, FakeRepositoryReader(None), "owner/app")
    assert [p.pass_id for p in result.report.passes_executed] == ["build", "repository_sync"]
    state = result.context.get(REPOSITORY_STATE)
    assert state.sync_status == "unpublished"
    # the one new report section: the sync status surfaces into the build log
    assert result.report.publisher_result == "unpublished"
    assert result.report.commit_sha is None


# --- The endpoint ---------------------------------------------------------------------------------

def test_repository_state_endpoint(client):
    app.dependency_overrides[get_repository_reader] = lambda: FakeRepositoryReader(None)
    pid = client.post("/api/v1/projects", json={"title": "App", "idea": "a FastAPI app"}).json()["id"]
    client.post(f"/api/v1/projects/{pid}/artifacts/vision")
    data = client.get(f"/api/v1/projects/{pid}/repository-state?repository=owner/app").json()
    assert data["sync_status"] == "unpublished"
    assert data["pending_artifacts"]


def test_repository_state_no_credential_400(client):
    app.dependency_overrides[get_repository_reader] = lambda: None
    pid = client.post("/api/v1/projects", json={"title": "App", "idea": "x"}).json()["id"]
    r = client.get(f"/api/v1/projects/{pid}/repository-state?repository=owner/app")
    assert r.status_code == 400


def test_repository_state_requires_auth(anon_client):
    r = anon_client.get("/api/v1/projects/whatever/repository-state?repository=owner/app")
    assert r.status_code == 401
