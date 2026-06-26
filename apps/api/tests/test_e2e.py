"""End-to-end happy path — the Day 10 journey: Vision -> PRD -> edit -> version history."""


def test_full_artifact_workflow(client):
    project_id = client.post(
        "/api/v1/projects",
        json={"title": "Engineering OS", "idea": "An AI workspace for software engineers"},
    ).json()["id"]

    # Generate the Vision.
    assert client.post(f"/api/v1/projects/{project_id}/artifacts/vision").status_code == 201

    # Generate the PRD from the Vision.
    assert client.post(f"/api/v1/projects/{project_id}/artifacts/prd").status_code == 201

    # Edit the PRD -> version 2.
    client.put(
        f"/api/v1/projects/{project_id}/artifacts/prd",
        json={"content": "# PRD\n\nEdited by the engineer."},
    )

    # Reopen later — persisted, edited content.
    reopened = client.get(f"/api/v1/projects/{project_id}/artifacts/prd").json()
    assert reopened["content"] == "# PRD\n\nEdited by the engineer."
    assert reopened["version"] == 2 and reopened["source"] == "human"

    # Version history is recorded (newest first).
    history = client.get(f"/api/v1/projects/{project_id}/artifacts/prd/versions").json()
    assert [v["version"] for v in history] == [2, 1]
