"""Credential port — the seam that keeps publishers ignorant of OAuth (ADR-0012).

A publisher knows only that it received a valid credential for its destination. *How* that
credential was obtained (a user's OAuth session today, a service token in CI tomorrow) lives
behind this port. This continues the dependency inversion the renderers/publishers split began:
`GitHubPublisher` never imports identity, sessions, or OAuth — it asks for a credential."""
from typing import Protocol


class MissingCredentialError(Exception):
    """No usable credential is available for the requested publisher type."""


class CredentialProvider(Protocol):
    def get_publishing_credential(self, publisher_type: str) -> str:
        """Return a credential for `publisher_type` ("github", later "gitlab", …), or raise
        MissingCredentialError. The caller builds the publisher's client from it."""
        ...
