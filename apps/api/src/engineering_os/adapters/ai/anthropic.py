"""Anthropic provider — the one real adapter for the MVP. SDK imported lazily so the rest of
the app (and tests with the fake) never require it."""
from ...ports.ai_provider import GenerationResult

_SYSTEM = (
    "You are a principal product engineer. Given a one-line product idea, write a concise, "
    "concrete product VISION in Markdown with sections: Problem, Vision, Why now, and What "
    "success looks like. Be specific and opinionated. No marketing language."
)


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def generate_vision(self, idea: str) -> GenerationResult:
        import anthropic  # lazy import — only needed when this provider is selected

        client = anthropic.Anthropic(api_key=self._api_key)
        message = client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=_SYSTEM,
            messages=[{"role": "user", "content": f"Product idea:\n{idea}\n\nWrite the Vision."}],
        )
        text = "".join(block.text for block in message.content if getattr(block, "type", "") == "text")
        return GenerationResult(
            content=text,
            model=self._model,
            tokens_in=message.usage.input_tokens,
            tokens_out=message.usage.output_tokens,
        )
