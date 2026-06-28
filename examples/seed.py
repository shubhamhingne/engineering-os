"""A runnable end-to-end example — no server, no GitHub app, no API key required.

    python examples/seed.py

It drives the API in-process (the fake OAuth + AI providers), creating a project and compiling its
artifacts, then prints what happened. This is the fastest way to see the whole pipeline work."""
import logging
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from engineering_os.main import app


def main() -> None:
    logging.getLogger().setLevel(logging.ERROR)  # quiet the request logs; show only the walkthrough
    client = TestClient(app)

    # 1. Sign in (fake GitHub OAuth — deterministic, no app needed).
    login = client.get("/api/v1/auth/github/login", follow_redirects=False)
    state = parse_qs(urlparse(login.headers["location"]).query)["state"][0]
    client.get("/api/v1/auth/github/callback",
               params={"code": "fake:demo", "state": state}, follow_redirects=False)

    # 2. Create a project.
    project = client.post(
        "/api/v1/projects",
        json={"title": "Acme API", "idea": "a FastAPI service with authentication and billing"},
    ).json()
    pid = project["id"]
    print(f"created project {pid!r}: {project['title']}")

    # 3. Compile artifacts: Vision → PRD → README (synthesized from the KnowledgeGraph).
    for artifact in ("vision", "prd", "readme"):
        v = client.post(f"/api/v1/projects/{pid}/artifacts/{artifact}").json()
        print(f"  generated {artifact:7} v{v['version']} ({len(v['content'])} chars)")

    # 4. Explain it — provenance for every entity (the differentiator).
    explanations = client.get(f"/api/v1/projects/{pid}/explanations").json()
    print(f"explanations: {len(explanations)} entities, e.g. "
          + ", ".join(e["entity_id"] for e in explanations[:3]))

    # 5. The build manifest — the compilation's immutable identity.
    manifest = client.get(f"/api/v1/projects/{pid}/build-manifest").json()
    print(f"manifest {manifest['manifest_hash']} · {len(manifest['artifact_hashes'])} artifacts")


if __name__ == "__main__":
    main()
