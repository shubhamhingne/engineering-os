"""ADR synthesis — DecisionGraph → ADR. Semantic, not markdown, tests."""
from engineering_os.modules.decision.service import DecisionExtractor
from engineering_os.modules.knowledge.service import KnowledgeExtractor


def _project_with_vision(client, idea: str):
    pid = client.post("/api/v1/projects", json={"title": "App", "idea": idea}).json()["id"]
    client.post(f"/api/v1/projects/{pid}/artifacts/vision")
    return pid


def test_decision_extractor_builds_typed_graph():
    graph = KnowledgeExtractor().extract("App", "a FastAPI app with authentication", {"vision": "# V\n\n## Vision\nx\n"})
    dg = DecisionExtractor().extract(graph)
    assert dg.schema_version == "v1"
    tech = next(d for d in dg.decisions if "technology" in d.title.lower())
    assert "FastAPI" in tech.decision and tech.sources


def test_adr_is_synthesized_with_structure_and_semantics(client):
    pid = _project_with_vision(client, "a FastAPI and PostgreSQL service")
    r = client.post(f"/api/v1/projects/{pid}/artifacts/adr")
    assert r.status_code == 201 and r.json()["type"] == "adr"
    content = r.json()["content"]
    assert "## Context" in content and "## Decision" in content and "## Consequences" in content
    assert "## Provenance" in content and "FastAPI" in content


def test_adr_requires_vision_409(client):
    pid = client.post("/api/v1/projects", json={"title": "T", "idea": "x"}).json()["id"]
    assert client.post(f"/api/v1/projects/{pid}/artifacts/adr").status_code == 409


def test_adr_is_not_streamable(client):
    pid = _project_with_vision(client, "x")
    assert client.post(f"/api/v1/projects/{pid}/artifacts/adr/stream").status_code == 400
