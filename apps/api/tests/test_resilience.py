"""Retry policy for transient external-call failures — the hardening behind every provider."""
import pytest

from engineering_os.resilience import call_with_retry


def _noop(_delay):
    return None


def test_succeeds_on_first_try_without_sleeping():
    calls = []
    assert call_with_retry(lambda: calls.append(1) or "ok", sleep=_noop) == "ok"
    assert len(calls) == 1


def test_retries_then_succeeds():
    state = {"n": 0}

    def flaky():
        state["n"] += 1
        if state["n"] < 3:
            raise ConnectionError("blip")
        return "ok"

    assert call_with_retry(flaky, attempts=3, retry_on=(ConnectionError,), sleep=_noop) == "ok"
    assert state["n"] == 3


def test_exhausts_attempts_then_raises():
    with pytest.raises(ConnectionError):
        call_with_retry(lambda: (_ for _ in ()).throw(ConnectionError("down")),
                        attempts=3, retry_on=(ConnectionError,), sleep=_noop)


def test_does_not_retry_unlisted_errors():
    calls = []

    def boom():
        calls.append(1)
        raise ValueError("permanent")

    with pytest.raises(ValueError):
        call_with_retry(boom, attempts=3, retry_on=(ConnectionError,), sleep=_noop)
    assert len(calls) == 1                                   # not retried


def test_backoff_is_exponential():
    delays: list = []
    with pytest.raises(ConnectionError):
        call_with_retry(lambda: (_ for _ in ()).throw(ConnectionError()),
                        attempts=3, base_delay=0.1, retry_on=(ConnectionError,), sleep=delays.append)
    assert delays == [0.1, 0.2]                              # two waits before the final attempt
