"""Real GitHub API client. Used only when a token is configured (Alpha-0.8 will add the user
OAuth flow). Tests exercise the publisher via the fake client, so this is never hit in CI."""
import base64

_API = "https://api.github.com"


class RealGitHubClient:
    def __init__(self, token: str) -> None:
        self._token = token

    def _client(self):
        import httpx  # lazy

        return httpx.Client(
            base_url=_API,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30,
        )

    def create_repo(self, name: str, private: bool) -> dict:
        with self._client() as client:
            res = client.post("/user/repos", json={"name": name, "private": private, "auto_init": False})
            res.raise_for_status()
            data = res.json()
            return {"full_name": data["full_name"], "html_url": data["html_url"]}

    def commit_files(self, full_name: str, files: dict, message: str) -> str:
        sha = ""
        with self._client() as client:
            for path, content in files.items():
                res = client.put(
                    f"/repos/{full_name}/contents/{path}",
                    json={"message": message, "content": base64.b64encode(content.encode("utf-8")).decode("ascii")},
                )
                res.raise_for_status()
                sha = res.json().get("commit", {}).get("sha", sha)
        return sha
