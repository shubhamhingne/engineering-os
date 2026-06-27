"""GitHub OAuth adapter (real) + a deterministic fake for tests/dev — mirroring the AI provider
split. `httpx` is imported lazily so the fake path never requires network libraries."""
from urllib.parse import urlencode

from ...ports.oauth import OAuthIdentity

_AUTHORIZE = "https://github.com/login/oauth/authorize"
_TOKEN = "https://github.com/login/oauth/access_token"
_USER = "https://api.github.com/user"


class GitHubOAuthProvider:
    """Real GitHub OAuth. Used only when client id/secret are configured. The `repo` scope is
    requested so the same token can later back the GitHub publisher (one consent, one token)."""

    name = "github"
    scope = "read:user repo"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri

    def authorize_url(self, state: str) -> str:
        query = urlencode(
            {
                "client_id": self._client_id,
                "redirect_uri": self._redirect_uri,
                "scope": self.scope,
                "state": state,
            }
        )
        return f"{_AUTHORIZE}?{query}"

    def exchange_code(self, code: str) -> str:
        import httpx

        resp = httpx.post(
            _TOKEN,
            headers={"Accept": "application/json"},
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "code": code,
                "redirect_uri": self._redirect_uri,
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        token = resp.json().get("access_token")
        if not token:
            raise ValueError("GitHub did not return an access token")
        return token

    def fetch_identity(self, access_token: str) -> OAuthIdentity:
        import httpx

        resp = httpx.get(
            _USER,
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return OAuthIdentity(
            github_id=str(data["id"]),
            username=data["login"],
            avatar_url=data.get("avatar_url", ""),
        )


class FakeOAuthProvider:
    """Deterministic OAuth for tests and local dev — no network. The callback `code` carries the
    desired identity (`code = "fake:<username>"`) so tests can authenticate distinct users."""

    name = "github"

    def authorize_url(self, state: str) -> str:
        return f"https://fake-oauth.local/authorize?state={state}"

    def exchange_code(self, code: str) -> str:
        username = code.split(":", 1)[1] if code.startswith("fake:") else "octocat"
        return f"fake-token-for-{username}"

    def fetch_identity(self, access_token: str) -> OAuthIdentity:
        username = access_token.rsplit("-", 1)[-1]
        return OAuthIdentity(
            github_id=f"gh_{username}",
            username=username,
            avatar_url=f"https://avatars.fake.local/{username}.png",
        )
