"""Identity, federation, and authorization (Alpha-0.8). The OAuth flow runs end to end against a
deterministic fake provider; ownership is enforced at the application boundary, never in the
compiler (ADR-0012)."""
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

from engineering_os.main import app
from engineering_os.modules.identity.credentials import GitHubCredentialProvider
from engineering_os.ports.credentials import MissingCredentialError


def _login(tc: TestClient, username: str) -> None:
    """Drive the real login → callback handshake; leaves a session cookie in the client's jar."""
    r = tc.get("/api/v1/auth/github/login", follow_redirects=False)
    assert r.status_code == 307
    state = parse_qs(urlparse(r.headers["location"]).query)["state"][0]
    cb = tc.get(
        "/api/v1/auth/github/callback",
        params={"code": f"fake:{username}", "state": state},
        follow_redirects=False,
    )
    assert cb.status_code == 307


# --- The CredentialProvider seam (publisher never sees OAuth) --------------------------------------

def test_credential_provider_returns_session_token():
    assert GitHubCredentialProvider("gho_abc").get_publishing_credential("github") == "gho_abc"


def test_credential_provider_rejects_unknown_publisher():
    with pytest.raises(MissingCredentialError):
        GitHubCredentialProvider("gho_abc").get_publishing_credential("gitlab")


def test_credential_provider_rejects_empty_token():
    with pytest.raises(MissingCredentialError):
        GitHubCredentialProvider("").get_publishing_credential("github")


# --- Token encryption at rest (BR-02) -------------------------------------------------------------

def test_token_cipher_round_trips_without_leaking_plaintext():
    from engineering_os.modules.identity.crypto import TokenCipher

    cipher = TokenCipher("a-test-key")
    ciphertext = cipher.encrypt("gho_secret_token")
    assert ciphertext != "gho_secret_token"
    assert "gho_secret_token" not in ciphertext
    assert cipher.decrypt(ciphertext) == "gho_secret_token"


def test_github_token_is_encrypted_at_rest(anon_client, db):
    from sqlalchemy import select

    from engineering_os.adapters.db.models import UserSession
    from engineering_os.modules.identity.service import IdentityService

    _login(anon_client, "alice")  # fake provider mints the plaintext token "fake-token-for-alice"
    row = db.scalars(select(UserSession)).first()
    assert row is not None
    assert row.github_token != "fake-token-for-alice"        # the column holds ciphertext
    assert "fake-token-for-alice" not in row.github_token
    assert IdentityService(db).decrypt_token(row) == "fake-token-for-alice"  # recovered only on demand


# --- Federation: the OAuth flow -------------------------------------------------------------------

def test_login_redirects_to_provider_with_state(anon_client):
    r = anon_client.get("/api/v1/auth/github/login", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"].startswith("https://fake-oauth.local/authorize")
    assert "state" in parse_qs(urlparse(r.headers["location"]).query)


def test_callback_with_bad_state_is_rejected(anon_client):
    # No prior login → no state cookie → callback must refuse.
    r = anon_client.get(
        "/api/v1/auth/github/callback", params={"code": "fake:alice", "state": "forged"}, follow_redirects=False
    )
    assert r.status_code == 400


def test_full_flow_authenticates_user(anon_client):
    _login(anon_client, "alice")
    me = anon_client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "alice"


def test_me_requires_authentication(anon_client):
    assert anon_client.get("/api/v1/auth/me").status_code == 401


def test_logout_ends_the_session(anon_client):
    _login(anon_client, "alice")
    assert anon_client.get("/api/v1/auth/me").status_code == 200
    anon_client.post("/api/v1/auth/logout")
    assert anon_client.get("/api/v1/auth/me").status_code == 401


# --- Authorization: a user owns their projects ----------------------------------------------------

def test_creating_a_project_requires_auth(anon_client):
    assert anon_client.post("/api/v1/projects", json={"title": "T", "idea": "x"}).status_code == 401


def test_projects_are_owner_scoped(anon_client, session_factory):
    # alice owns a project; bob (a separate session) can neither see nor read it.
    _login(anon_client, "alice")
    pid = anon_client.post("/api/v1/projects", json={"title": "A", "idea": "a FastAPI app"}).json()["id"]

    bob = TestClient(app)
    _login(bob, "bob")
    assert bob.get(f"/api/v1/projects/{pid}").status_code == 403
    assert bob.get("/api/v1/projects").json() == []          # bob's list excludes alice's project
    assert anon_client.get(f"/api/v1/projects/{pid}").status_code == 200  # alice still owns it
