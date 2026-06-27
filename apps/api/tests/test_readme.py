"""README synthesis — semantic (not markdown) tests, quality score, and provenance."""


def _project_with_vision(client, idea: str):
    pid = client.post("/api/v1/projects", json={"title": "App", "idea": idea}).json()["id"]
    client.post(f"/api/v1/projects/{pid}/artifacts/vision")
    return pid


def test_readme_reflects_authentication_from_the_vision(client):
    pid = _project_with_vision(client, "a tool with authentication and billing")
    r = client.post(f"/api/v1/projects/{pid}/artifacts/readme")
    assert r.status_code == 201 and r.json()["type"] == "readme"
    content = r.json()["content"].lower()
    # semantic: the topic surfaced from the artifacts must appear in the README
    assert "authentication" in content
    # structure: synthesized sections present
    assert "## problem" in content and "## features" in content and "## tech stack" in content


def test_readme_detects_tech_stack(client):
    pid = _project_with_vision(client, "a FastAPI and PostgreSQL backend service")
    content = client.post(f"/api/v1/projects/{pid}/artifacts/readme").json()["content"]
    assert "FastAPI" in content and "PostgreSQL" in content


def test_readme_requires_vision_409(client):
    pid = client.post("/api/v1/projects", json={"title": "T", "idea": "x"}).json()["id"]
    assert client.post(f"/api/v1/projects/{pid}/artifacts/readme").status_code == 409


def test_readme_quality_score_and_missing(client):
    pid = _project_with_vision(client, "an idea")
    q = client.get(f"/api/v1/projects/{pid}/artifacts/readme/quality").json()
    assert 0 <= q["score"] <= 100
    assert "Screenshots" in q["missing"]  # no images captured yet → always flagged
    assert isinstance(q["provenance"], dict)


def test_readme_is_not_streamable(client):
    pid = _project_with_vision(client, "x")
    assert client.post(f"/api/v1/projects/{pid}/artifacts/readme/stream").status_code == 400
