"""Integration tests — the artifact-centric API with a test DB and the fake provider."""


def _new_project(client):
    return client.post("/api/v1/projects", json={"title": "T", "idea": "an idea"}).json()["id"]


def test_create_list_get(client):
    created = client.post("/api/v1/projects", json={"title": "T", "idea": "an idea"})
    assert created.status_code == 201
    project_id = created.json()["id"]
    assert len(client.get("/api/v1/projects").json()) == 1
    fetched = client.get(f"/api/v1/projects/{project_id}")
    assert fetched.status_code == 200 and fetched.json()["artifact_types"] == []


def test_create_validation_rejects_empty(client):
    assert client.post("/api/v1/projects", json={"title": "", "idea": ""}).status_code == 422


def test_unsupported_artifact_type_404(client):
    project_id = _new_project(client)
    assert client.post(f"/api/v1/projects/{project_id}/artifacts/adr").status_code == 404


def test_prd_requires_vision_409(client):
    project_id = _new_project(client)
    assert client.post(f"/api/v1/projects/{project_id}/artifacts/prd").status_code == 409


def test_vision_then_prd_flow(client):
    project_id = _new_project(client)
    vision = client.post(f"/api/v1/projects/{project_id}/artifacts/vision")
    assert vision.status_code == 201 and vision.json()["type"] == "vision" and vision.json()["version"] == 1

    prd = client.post(f"/api/v1/projects/{project_id}/artifacts/prd")
    assert prd.status_code == 201 and prd.json()["type"] == "prd"
    assert "# Product Requirements Document" in prd.json()["content"]

    types = client.get(f"/api/v1/projects/{project_id}").json()["artifact_types"]
    assert sorted(types) == ["prd", "vision"]


def test_stream_vision_emits_stages_and_persists(client):
    project_id = _new_project(client)
    with client.stream("POST", f"/api/v1/projects/{project_id}/artifacts/vision/stream") as r:
        assert r.status_code == 200
        body = "".join(r.iter_text())
    assert "event: stage" in body
    assert "event: token" in body
    assert "event: done" in body
    # the streamed content was persisted as a version
    got = client.get(f"/api/v1/projects/{project_id}/artifacts/vision")
    assert got.status_code == 200 and "# Product Vision" in got.json()["content"]


def test_stream_prd_requires_vision_409(client):
    project_id = _new_project(client)
    assert client.post(f"/api/v1/projects/{project_id}/artifacts/prd/stream").status_code == 409


def test_edit_creates_version_and_history(client):
    project_id = _new_project(client)
    client.post(f"/api/v1/projects/{project_id}/artifacts/vision")
    saved = client.put(
        f"/api/v1/projects/{project_id}/artifacts/vision", json={"content": "edited"}
    ).json()
    assert saved["version"] == 2 and saved["source"] == "human"

    versions = client.get(f"/api/v1/projects/{project_id}/artifacts/vision/versions").json()
    assert [v["version"] for v in versions] == [2, 1]
