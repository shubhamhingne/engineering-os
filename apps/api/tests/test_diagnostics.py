"""Production diagnostics (Sprint 3) — request correlation, trace ids on failures, and metrics.
The mission: a production failure is diagnosable from the response alone."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from engineering_os.main import unhandled_exception_handler
from engineering_os.metrics import estimate_cost_usd


def test_every_response_carries_a_request_id(client):
    assert client.get("/health/live").headers.get("x-request-id")


def test_incoming_request_id_is_propagated(client):
    r = client.get("/health/live", headers={"X-Request-ID": "abc123"})
    assert r.headers["x-request-id"] == "abc123"


def test_metrics_endpoint_exposes_http_and_ai_series(client):
    pid = client.post("/api/v1/projects", json={"title": "T", "idea": "a FastAPI app"}).json()["id"]
    client.post(f"/api/v1/projects/{pid}/artifacts/vision")     # populate AI metrics
    body = client.get("/metrics").text
    assert "eos_http_requests_total" in body
    assert "eos_http_request_duration_seconds" in body
    assert "eos_ai_generations_total" in body
    assert "eos_ai_tokens_total" in body


def test_unhandled_exception_returns_a_trace_id():
    app = FastAPI()
    app.add_exception_handler(Exception, unhandled_exception_handler)

    @app.get("/boom")
    def boom():
        raise RuntimeError("kaboom")

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/boom")
    assert r.status_code == 500
    body = r.json()
    assert body["detail"] == "internal server error"
    assert len(body["trace_id"]) == 32                          # a correlatable id, returned to the caller


def test_cost_estimate_is_zero_for_unknown_models_and_priced_for_known():
    assert estimate_cost_usd("fake-1", 1000, 1000) == 0.0
    assert estimate_cost_usd("claude-sonnet-4-6", 1000, 1000) > 0
