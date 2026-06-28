"""Abuse protection (BR-05): a sliding-window rate limiter applied to the expensive/spoofable routes
(AI generation, the OAuth callback). Off in dev/tests; the production profile turns it on.

In-memory and per-process — correct for a single instance; a Redis-backed store is the drop-in for
horizontal scale (the same swap the pass cache anticipates). Keyed by session when present, else by
client IP."""
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from ...config import settings


def _client_key(request: Request) -> str:
    sid = request.cookies.get(settings.session_cookie)
    if sid:
        return f"sess:{sid}"
    client = request.client
    return f"ip:{client.host if client else 'unknown'}"


class RateLimit:
    """A callable FastAPI dependency. One instance per route group keeps independent budgets."""

    def __init__(self, group: str) -> None:
        self._group = group
        self._hits: dict = defaultdict(deque)

    def __call__(self, request: Request) -> None:
        if not settings.rate_limit_enabled:
            return
        limit = settings.rate_limit_per_minute
        now = time.monotonic()
        bucket = self._hits[f"{self._group}:{_client_key(request)}"]
        while bucket and bucket[0] <= now - 60.0:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(status_code=429, detail="rate limit exceeded — slow down")
        bucket.append(now)

    def reset(self) -> None:
        self._hits.clear()


generation_rate_limit = RateLimit("generation")
auth_rate_limit = RateLimit("auth")
