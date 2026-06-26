"""End-to-end happy path — the exact Day 9 user journey, proven against the API.

Create project -> generate Vision -> edit -> save -> reopen later (persisted).
"""


def test_full_vision_workflow(client):
    # 1. Create a project from an idea.
    project_id = client.post(
        "/api/v1/projects",
        json={"title": "Engineering OS", "idea": "An AI workspace for software engineers"},
    ).json()["id"]

    # 2. Generate a Vision.
    assert client.post(f"/api/v1/projects/{project_id}/vision").status_code == 201

    # 3. Edit and save.
    client.put(
        f"/api/v1/projects/{project_id}/vision",
        json={"content": "# Vision\n\nA focused, edited vision."},
    )

    # 4. Reopen later — a fresh fetch returns the persisted, edited content.
    reopened = client.get(f"/api/v1/projects/{project_id}/vision").json()
    assert reopened["content"] == "# Vision\n\nA focused, edited vision."
    assert reopened["version"] == 2 and reopened["source"] == "human"

    # The project reflects that it has a vision.
    assert client.get(f"/api/v1/projects/{project_id}").json()["has_vision"] is True
