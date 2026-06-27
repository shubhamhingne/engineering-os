"""GitHubCredentialProvider — the concrete CredentialProvider for the OAuth session.

It holds the session's GitHub token and hands it to whoever is building the GitHub publisher's
client. The publisher stays oblivious to OAuth; it receives a credential and nothing else. A future
GitLabCredentialProvider slots in here without touching either the publisher or the compiler."""
from ...ports.credentials import MissingCredentialError


class GitHubCredentialProvider:
    def __init__(self, github_token: str) -> None:
        self._github_token = github_token

    def get_publishing_credential(self, publisher_type: str) -> str:
        if publisher_type != "github":
            raise MissingCredentialError(f"no credential for publisher '{publisher_type}'")
        if not self._github_token:
            raise MissingCredentialError("no GitHub credential on this session")
        return self._github_token
