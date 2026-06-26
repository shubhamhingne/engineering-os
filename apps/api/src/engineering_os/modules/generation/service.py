"""Generation module. Orchestrates an AI run through the port and emits observability."""
import logging
import time

from ...ports.ai_provider import AIProvider, GenerationResult

log = logging.getLogger("eos.generation")


class GenerationService:
    def __init__(self, provider: AIProvider) -> None:
        self._provider = provider

    def generate_vision(self, idea: str) -> GenerationResult:
        if not idea or not idea.strip():
            raise ValueError("idea must not be empty")

        started = time.perf_counter()
        result = self._provider.generate_vision(idea)
        latency_ms = int((time.perf_counter() - started) * 1000)

        # Every AI action is observable (Principle 4).
        log.info(
            "vision.generated",
            extra={
                "provider": self._provider.name,
                "model": result.model,
                "tokens_in": result.tokens_in,
                "tokens_out": result.tokens_out,
                "latency_ms": latency_ms,
            },
        )
        return result
