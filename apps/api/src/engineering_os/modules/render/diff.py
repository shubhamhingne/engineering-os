"""Diff engine — compare a previous bundle (path → content) against a new bundle by hash, so a
publisher can ship only what changed instead of pushing everything (ADR-0010)."""
import hashlib
from dataclasses import dataclass, field

from .renderers import ArtifactBundle


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]


@dataclass
class BundleDiff:
    added: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.added or self.changed or self.removed)


class DiffEngine:
    def diff(self, previous: dict[str, str], current: ArtifactBundle) -> BundleDiff:
        prev = {path: _hash(content) for path, content in previous.items()}
        cur = {artifact.path: artifact.hash for artifact in current.artifacts}
        result = BundleDiff()
        for path, digest in cur.items():
            if path not in prev:
                result.added.append(path)
            elif prev[path] != digest:
                result.changed.append(path)
            else:
                result.unchanged.append(path)
        for path in prev:
            if path not in cur:
                result.removed.append(path)
        for bucket in (result.added, result.changed, result.unchanged, result.removed):
            bucket.sort()
        return result
