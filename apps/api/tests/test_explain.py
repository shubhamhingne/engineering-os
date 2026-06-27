"""Explainability — the ExplanationGraph compiler output + the pass pipeline."""
import pytest

from engineering_os.modules.compiler.passes import ExtractKnowledgePass, PassRunner, run_explain_pipeline


def test_explain_pipeline_produces_explanations_with_provenance():
    sources = {
        "vision": "# V\n\n## Problem\nthe product needs authentication\n",
        "prd": "# P\n\n## Requirements\n- a FastAPI service\n",
    }
    graph = run_explain_pipeline("App", "a FastAPI app with authentication", sources)
    ids = {e.entity_id for e in graph.explanations}
    assert "topic:authentication" in ids and "tech:FastAPI" in ids

    auth = graph.get("topic:authentication")
    assert auth is not None
    assert auth.confidence > 0
    assert "vision" in auth.sources              # evidence: where it was mentioned
    assert any(p.endswith(".md") for p in auth.appears_in)  # provenance: produced artifacts


def test_pass_runner_validates_required_inputs():
    with pytest.raises(ValueError):
        PassRunner().run([ExtractKnowledgePass()], {})  # missing title/idea/sources


def test_explanations_endpoint(client):
    pid = client.post(
        "/api/v1/projects", json={"title": "App", "idea": "a FastAPI app with authentication"}
    ).json()["id"]
    client.post(f"/api/v1/projects/{pid}/artifacts/vision")
    data = client.get(f"/api/v1/projects/{pid}/explanations").json()
    ids = {e["entity_id"] for e in data}
    assert "topic:authentication" in ids and "tech:FastAPI" in ids
    auth = next(e for e in data if e["entity_id"] == "topic:authentication")
    assert auth["confidence"] > 0 and auth["appears_in"]
