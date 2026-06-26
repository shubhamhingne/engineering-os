"""Anthropic provider — the one real adapter for the MVP. SDK imported lazily so the rest of
the app (and tests with the fake) never require it."""
from ...ports.ai_provider import GenerationResult, Prompt


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def generate(self, prompt: Prompt) -> GenerationResult:
        import anthropic  # lazy import — only needed when this provider is selected

        client = anthropic.Anthropic(api_key=self._api_key)
        message = client.messages.create(
            model=self._model,
            max_tokens=1500,
            system=prompt.system,
            messages=[{"role": "user", "content": prompt.user}],
        )
        text = "".join(b.text for b in message.content if getattr(b, "type", "") == "text")
        return GenerationResult(
            content=text,
            model=self._model,
            tokens_in=message.usage.input_tokens,
            tokens_out=message.usage.output_tokens,
        )
