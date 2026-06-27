"""RepositoryState — the remote analogue of CompilationReport (ADR-0015).

It models *the state of publication*, independent of transport: which commit is published, what the
remote holds, and whether local and remote agree. GitHub is one implementation; nothing here knows
about GitHub. `build_repository_state` is a pure comparison — testable without any network."""
from dataclasses import dataclass, field
from typing import Optional

from ...ports.repository import RemoteSnapshot

# Publication status — purely a function of (local bundle hashes, remote snapshot).
UNPUBLISHED = "unpublished"   # the remote does not exist yet
IN_SYNC = "in_sync"           # every local artifact matches the remote
AHEAD = "ahead"              # local has artifacts the remote lacks or that differ (pending upload)


@dataclass
class RepositoryState:
    repository: str
    default_branch: str
    published_commit: Optional[str]
    remote_artifact_hashes: dict          # path -> hash, as last observed on the remote
    sync_status: str
    pending_artifacts: list = field(default_factory=list)   # local paths not yet matching the remote
    last_sync: Optional[str] = None       # filled once sync history is persisted
    remote_fingerprint: Optional[str] = None   # the remote's compiler fingerprint, when exposed
    diagnostics: list = field(default_factory=list)
    schema_version: str = "v1"


def build_repository_state(
    repository: str, local_hashes: dict, snapshot: Optional[RemoteSnapshot]
) -> RepositoryState:
    """Compare the local bundle's hashes against the remote snapshot. Observation only — this makes
    no decision about whether or what to publish."""
    if snapshot is None:
        return RepositoryState(
            repository=repository,
            default_branch="",
            published_commit=None,
            remote_artifact_hashes={},
            sync_status=UNPUBLISHED,
            pending_artifacts=sorted(local_hashes),
            diagnostics=[f"{repository} has not been published yet"],
        )

    remote = snapshot.artifact_hashes
    pending = sorted(path for path, h in local_hashes.items() if remote.get(path) != h)
    removed = sorted(path for path in remote if path not in local_hashes)
    status = IN_SYNC if not pending and not removed else AHEAD

    diagnostics: list = []
    if pending:
        diagnostics.append(f"{len(pending)} artifact(s) to publish: {pending}")
    if removed:
        diagnostics.append(f"{len(removed)} remote artifact(s) absent from the local bundle: {removed}")

    return RepositoryState(
        repository=repository,
        default_branch=snapshot.default_branch,
        published_commit=snapshot.head_commit,
        remote_artifact_hashes=dict(remote),
        sync_status=status,
        pending_artifacts=pending,
        diagnostics=diagnostics,
    )
