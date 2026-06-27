"""Read-only remote-repository port (ADR-0015).

`RepositorySyncPass` *observes* the remote through this port — it never publishes. Reading remote
state and deciding what to transmit are different jobs: the planner decides what to build, the
publisher decides how to transmit, and this port answers only "what does the remote look like now?"
GitHub is one adapter; the port leaves room for others without touching the compiler."""
from dataclasses import dataclass, field
from typing import Optional, Protocol


@dataclass
class RemoteSnapshot:
    """What the remote currently holds — the raw observation, before comparison to local."""

    repository: str
    default_branch: str
    head_commit: Optional[str]
    artifact_hashes: dict = field(default_factory=dict)   # path -> content hash (our hash scheme)


class RepositoryReader(Protocol):
    def read_state(self, repository: str) -> Optional[RemoteSnapshot]:
        """Return the remote's current state, or None if the repository does not exist yet."""
        ...
