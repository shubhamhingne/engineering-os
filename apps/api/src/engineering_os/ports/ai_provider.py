"""The AI provider port. The core builds prompts (its opinion); the provider just executes one.
This keeps prompt logic in the domain and providers trivially swappable (Principle 5)."""
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class Prompt:
    system: str
    user: str
    artifact_type: str  # carried for observability + provider-side tuning


@dataclass
class GenerationResult:
    content: str
    model: str
    tokens_in: int = 0
    tokens_out: int = 0


@runtime_checkable
class AIProvider(Protocol):
    name: str

    def generate(self, prompt: Prompt) -> GenerationResult:
        """Execute a prompt and return the generated Markdown plus usage."""
        ...
