"""Generation module. Owns the prompt templates (the product's opinion) and orchestrates a
run through the AI port. Emits artifact-centric observability (Principle 4)."""
import logging
import time
from collections.abc import Iterator

from ...metrics import record_ai_generation
from ...ports.ai_provider import AIProvider, GenerationResult, Prompt

log = logging.getLogger("eos.generation")

_SYSTEM = {
    "vision": (
        "You are a principal product engineer. Given a one-line product idea, write a concise, "
        "concrete product VISION in Markdown with sections: Problem, Vision, Why now, and What "
        "success looks like. Be specific and opinionated. No marketing language."
    ),
    "prd": (
        "You are a principal product engineer. Given a product Vision, write a focused PRD in "
        "Markdown with sections: Overview, Goals, Non-goals, Requirements, and Risks. Keep scope "
        "tight and decisions explicit. No marketing language."
    ),
}


class GenerationService:
    def __init__(self, provider: AIProvider) -> None:
        self._provider = provider
        self.last_model: str = getattr(provider, "model", provider.name)

    def _build_prompt(self, artifact_type: str, context: dict[str, str]) -> Prompt:
        if artifact_type == "vision":
            idea = context.get("idea", "").strip()
            if not idea:
                raise ValueError("idea must not be empty")
            user = f"Product idea:\n{idea}\n\nWrite the Vision."
        elif artifact_type == "prd":
            vision = context.get("vision", "").strip()
            if not vision:
                raise ValueError("a Vision is required to generate a PRD")
            user = f"Product Vision:\n{vision}\n\nWrite the PRD."
        else:
            raise ValueError(f"unsupported artifact type: {artifact_type}")
        return Prompt(system=_SYSTEM[artifact_type], user=user, artifact_type=artifact_type)

    def generate(self, artifact_type: str, context: dict[str, str]) -> GenerationResult:
        prompt = self._build_prompt(artifact_type, context)
        started = time.perf_counter()
        result = self._provider.generate(prompt)
        latency_ms = int((time.perf_counter() - started) * 1000)
        log.info(
            "artifact.generated",
            extra={
                "artifact_type": artifact_type,
                "provider": self._provider.name,
                "model": result.model,
                "tokens_in": result.tokens_in,
                "tokens_out": result.tokens_out,
                "latency_ms": latency_ms,
            },
        )
        record_ai_generation(
            self._provider.name, result.model, artifact_type,
            result.tokens_in, result.tokens_out, latency_ms,
        )
        return result

    def stream(self, artifact_type: str, context: dict[str, str]) -> Iterator[str]:
        """Yield content chunks for a generation. The caller accumulates and persists."""
        prompt = self._build_prompt(artifact_type, context)
        self.last_model = getattr(self._provider, "model", self._provider.name)
        for chunk in self._provider.stream(prompt):
            yield chunk
