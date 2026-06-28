"""Operational hardening — health probes (BR-06), the production config guard (BR-07), and rate
limiting (BR-05). These are the deployability concerns, tested where they can be tested in-process."""
import pytest
from pydantic import ValidationError

from engineering_os.config import Settings, settings
from engineering_os.interface.http.ratelimit import generation_rate_limit


# --- Health probes (BR-06) ------------------------------------------------------------------------

def test_liveness_is_ok(client):
    assert client.get("/health/live").json()["status"] == "ok"
    assert client.get("/health").json()["status"] == "ok"   # back-compat alias


def test_readiness_ok_when_db_reachable(client):
    r = client.get("/health/ready")
    assert r.status_code == 200 and r.json()["status"] == "ready"


def test_readiness_503_when_db_unreachable(client, monkeypatch):
    import engineering_os.main as main

    def boom():
        raise RuntimeError("database down")

    monkeypatch.setattr(main, "SessionLocal", boom)
    r = client.get("/health/ready")
    assert r.status_code == 503 and r.json()["status"] == "not ready"


# --- Production config guard (BR-07) --------------------------------------------------------------

def test_production_rejects_insecure_config():
    with pytest.raises(ValidationError):
        Settings(app_env="production", token_encryption_key="", database_url="sqlite:///./x.db")


def test_production_enforces_secure_defaults():
    s = Settings(
        app_env="production",
        token_encryption_key="a-real-secret",
        database_url="postgresql://u:p@db/eos",
    )
    assert s.cookie_secure is True and s.rate_limit_enabled is True


def test_development_stays_permissive():
    s = Settings(app_env="development")
    assert s.cookie_secure is False and s.rate_limit_enabled is False


# --- Rate limiting (BR-05) ------------------------------------------------------------------------

def test_rate_limit_blocks_after_threshold(client, monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 2)
    generation_rate_limit.reset()

    pid = client.post("/api/v1/projects", json={"title": "T", "idea": "a FastAPI app"}).json()["id"]
    codes = [client.post(f"/api/v1/projects/{pid}/artifacts/vision").status_code for _ in range(3)]
    assert codes[:2] == [201, 201]
    assert codes[2] == 429                                    # third call over the limit is throttled
    generation_rate_limit.reset()


def test_rate_limit_off_by_default(client):
    # Default settings → limiter is a no-op, so repeated generation is never throttled.
    pid = client.post("/api/v1/projects", json={"title": "T", "idea": "a FastAPI app"}).json()["id"]
    codes = [client.post(f"/api/v1/projects/{pid}/artifacts/vision").status_code for _ in range(4)]
    assert all(c == 201 for c in codes)
