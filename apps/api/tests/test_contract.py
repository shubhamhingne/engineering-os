"""API contract tests — guard the HTTP surface the frontend (and external integrators) depend on, so
a breaking change to a path or response shape fails CI rather than a client in production."""
from engineering_os.main import app

CRITICAL_PATHS = [
    "/health/ready",
    "/metrics",
    "/api/v1/projects",
    "/api/v1/projects/{project_id}",
    "/api/v1/projects/{project_id}/artifacts/{artifact_type}",
    "/api/v1/projects/{project_id}/explanations",
    "/api/v1/projects/{project_id}/build-manifest",
    "/api/v1/projects/{project_id}/repository-state",
    "/api/v1/auth/github/callback",
]


def test_critical_endpoints_are_in_the_contract():
    paths = app.openapi()["paths"]
    missing = [p for p in CRITICAL_PATHS if p not in paths]
    assert not missing, f"contract regression — missing endpoints: {missing}"


def test_project_response_shape_is_stable():
    schemas = app.openapi()["components"]["schemas"]
    project = schemas["ProjectOut"]["properties"]
    for field in ("id", "title", "idea", "artifact_types", "created_at", "updated_at"):
        assert field in project, f"ProjectOut lost field: {field}"


def test_build_manifest_shape_is_stable():
    manifest = app.openapi()["components"]["schemas"]["BuildManifestOut"]["properties"]
    for field in ("manifest_hash", "compiler_fingerprint", "plan_id", "report_id", "artifact_hashes"):
        assert field in manifest, f"BuildManifestOut lost field: {field}"
