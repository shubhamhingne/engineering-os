"""OAuth federation port. The application layer authenticates a user through *some* provider;
the core never depends on which one. GitHub is the first adapter; GitLab/Bitbucket are future
adapters behind this same contract (ADR-0012)."""
from dataclasses import dataclass
from typing import Protocol


@dataclass
class OAuthIdentity:
    """The minimal identity a provider returns — enough to be a User, nothing more."""

    github_id: str
    username: str
    avatar_url: str


class OAuthProvider(Protocol):
    def authorize_url(self, state: str) -> str:
        """The provider URL to redirect the browser to (carrying an anti-CSRF `state`)."""
        ...

    def exchange_code(self, code: str) -> str:
        """Exchange the callback `code` for a provider access token."""
        ...

    def fetch_identity(self, access_token: str) -> OAuthIdentity:
        """Resolve the access token to the authenticated user's identity."""
        ...
