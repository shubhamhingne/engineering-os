"""Resilience for external calls — bounded retry with exponential backoff.

Wraps the network-touching adapters (AI providers, the GitHub API) so a transient failure is retried
rather than surfaced to the user. The fakes used in tests never fail, so this is transparent in
dev/tests; the policy itself is a pure function, unit-tested independently of any network."""
import time
from typing import Callable, Optional, Tuple, Type, TypeVar

T = TypeVar("T")


def call_with_retry(
    fn: Callable[[], T],
    *,
    attempts: int = 3,
    base_delay: float = 0.2,
    retry_on: Tuple[Type[BaseException], ...] = (Exception,),
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Call `fn`, retrying on `retry_on` with exponential backoff. Re-raises the last error after
    `attempts` tries. `sleep` is injectable so tests don't actually wait."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    last_error: Optional[BaseException] = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except retry_on as exc:
            last_error = exc
            if attempt == attempts:
                raise
            sleep(base_delay * (2 ** (attempt - 1)))
    raise last_error  # pragma: no cover - loop always returns or raises
