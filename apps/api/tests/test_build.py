"""Build planner, artifact hashing, and the diff engine — the incremental-build phase."""
from engineering_os.modules.knowledge.service import KnowledgeExtractor
from engineering_os.modules.render.diff import DiffEngine
from engineering_os.modules.render.planner import BuildPlanner
from engineering_os.modules.render.renderers import RenderContext, RendererRegistry


def test_planner_skips_when_inputs_missing():
    graph = KnowledgeExtractor().extract("App", "an idea", {})
    plan = BuildPlanner().plan(graph, {})
    by = {i.renderer: i for i in plan.items}
    assert by["readme"].build is True
    assert by["adr"].build is False and by["docs"].build is False and by["openapi"].build is False


def test_planner_builds_when_inputs_present():
    present = {"vision": "# V\n\n## Vision\nx\n"}
    graph = KnowledgeExtractor().extract("App", "a FastAPI app", present)
    plan = BuildPlanner().plan(graph, present)
    assert {"readme", "adr", "docs", "scaffold"} <= plan.to_build()


def test_artifacts_are_hashed():
    bundle = RendererRegistry().build(RenderContext("A", "x", {}))
    assert all(len(a.hash) == 12 for a in bundle.artifacts)


def test_diff_engine_detects_changes():
    ctx = RenderContext("App", "a FastAPI app", {"vision": "# V\n\n## Vision\nx\n"})
    bundle = RendererRegistry().build(ctx)
    baseline = bundle.files()

    assert not DiffEngine().diff(baseline, bundle).has_changes()

    changed = dict(baseline)
    changed["README.md"] = "# different"
    diff = DiffEngine().diff(changed, bundle)
    assert "README.md" in diff.changed and diff.has_changes()

    with_extra = dict(baseline)
    with_extra["EXTRA.md"] = "x"
    assert "EXTRA.md" in DiffEngine().diff(with_extra, bundle).removed


def test_build_plan_endpoint(client):
    pid = client.post("/api/v1/projects", json={"title": "T", "idea": "a FastAPI app"}).json()["id"]
    client.post(f"/api/v1/projects/{pid}/artifacts/vision")
    by = {i["renderer"]: i for i in client.get(f"/api/v1/projects/{pid}/build-plan").json()["items"]}
    assert by["readme"]["build"] is True and by["adr"]["build"] is True


def test_export_diff_endpoint_tracks_state(client):
    pid = client.post("/api/v1/projects", json={"title": "T", "idea": "a FastAPI app"}).json()["id"]
    client.post(f"/api/v1/projects/{pid}/artifacts/vision")

    first = client.get(f"/api/v1/projects/{pid}/export/diff").json()
    assert "README.md" in first["added"] and first["has_changes"] is True

    with client.stream("POST", f"/api/v1/projects/{pid}/export/stream") as r:
        "".join(r.iter_text())

    after = client.get(f"/api/v1/projects/{pid}/export/diff").json()
    assert after["has_changes"] is False and "README.md" in after["unchanged"]
