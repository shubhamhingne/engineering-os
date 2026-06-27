"""Pass-output cache (ADR-0016).

The compiler already collects everything a cache needs — pass id, pass version, input hash, and the
compiler fingerprint. This turns that metadata into reuse. The cache key binds all four, so a hit is
only ever served when the same pass *version*, on the same *inputs*, under the same *compiler*, has
run before. The cache is injected at the boundary (a long-lived worker opts in; per-request handlers
stay cache-less and deterministic) — the same dependency-injection stance as every other adapter."""
from typing import Optional, Protocol


class PassCache(Protocol):
    def get(self, key: str) -> Optional[dict]:
        """Return the cached produced-slots dict ({ContextKey: value}) for `key`, or None."""
        ...

    def put(self, key: str, outputs: dict) -> None:
        ...


class InMemoryPassCache:
    """Process-local cache — correct because cacheable passes are deterministic and never mutate
    their inputs, so sharing produced objects across compilations is safe. A persistent
    (serialized) cache is a drop-in implementation of the same port."""

    def __init__(self) -> None:
        self._store: dict[str, dict] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[dict]:
        if key in self._store:
            self.hits += 1
            return self._store[key]
        self.misses += 1
        return None

    def put(self, key: str, outputs: dict) -> None:
        self._store[key] = outputs
