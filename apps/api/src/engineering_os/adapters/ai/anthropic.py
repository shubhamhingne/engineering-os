"""Anthropic provider — the one real adapter for the MVP. SDK imported lazily so the rest of
the app (and tests with the fake) never require it."""
from collections.abc import Iterator

from ...config import settings
from ...ports.ai_provider import GenerationResult, Prompt
from ...resilience import call_with_retry


def _transient_errors() -> tuple:
    """Anthropic's retryable failures (connection blips, rate limits, 5xx)."""
    import anthropic

    return (anthropic.APIConnectionError, anthropic.RateLimitError, anthropic.InternalServerError)


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self.model = model

    def _client(self):
        import anthropic  # lazy import — only needed when this provider is selected

        return anthropic.Anthropic(api_key=self._api_key)

    def generate(self, prompt: Prompt) -> GenerationResult:
        message = call_with_retry(
            lambda: self._client().messages.create(
                model=self.model,
                max_tokens=1500,
                system=prompt.system,
                messages=[{"role": "user", "content": prompt.user}],
            ),
            attempts=settings.external_retry_attempts,
            retry_on=_transient_errors(),
        )
        text = "".join(b.text for b in message.content if getattr(b, "type", "") == "text")
        return GenerationResult(
            content=text,
            model=self.model,
            tokens_in=message.usage.input_tokens,
            tokens_out=message.usage.output_tokens,
        )

    def stream(self, prompt: Prompt) -> Iterator[str]:
        with self._client().messages.stream(
            model=self.model,
            max_tokens=1500,
            system=prompt.system,
            messages=[{"role": "user", "content": prompt.user}],
        ) as stream:
            for text in stream.text_stream:
                yield text
