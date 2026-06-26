"""Integration tests — the API with a test DB and the fake provider."""


def test_create_list_get(client):
    created = client.post("/api/v1/projects", json={"title": "T", "idea": "an idea"})
    assert created.status_code == 201
    project_id = created.json()["id"]

    listing = client.get("/api/v1/projects")
    assert listing.status_code == 200 and len(listing.json()) == 1

    fetched = client.get(f"/api/v1/projects/{project_id}")
    assert fetched.status_code == 200 and fetched.json()["idea"] == "an idea"


def test_create_validation_rejects_empty(client):
    assert client.post("/api/v1/projects", json={"title": "", "idea": ""}).status_code == 422


def test_get_missing_project_404(client):
    assert client.get("/api/v1/projects/missing").status_code == 404


def test_vision_generate_then_get_then_save(client):
    project_id = client.post("/api/v1/projects", json={"title": "T", "idea": "an idea"}).json()["id"]

    generated = client.post(f"/api/v1/projects/{project_id}/vision")
    assert generated.status_code == 201 and generated.json()["source"] == "ai"

    fetched = client.get(f"/api/v1/projects/{project_id}/vision")
    assert fetched.status_code == 200 and "# Product Vision" in fetched.json()["content"]

    saved = client.put(f"/api/v1/projects/{project_id}/vision", json={"content": "my edit"})
    body = saved.json()
    assert saved.status_code == 200 and body["source"] == "human" and body["version"] == 2


def test_get_vision_before_generation_404(client):
    project_id = client.post("/api/v1/projects", json={"title": "T", "idea": "x"}).json()["id"]
    assert client.get(f"/api/v1/projects/{project_id}/vision").status_code == 404
