"""The AI provider port. The core builds prompts (its opinion); the provider executes one,
either all at once (`generate`) or as a token stream (`stream`). Keeps prompt logic in the
domain and providers trivially swappable (Principle 5)."""
from collections.abc import Iterator
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
    model: str

    def generate(self, prompt: Prompt) -> GenerationResult:
        """Execute a prompt and return the generated Markdown plus usage."""
        ...

    def stream(self, prompt: Prompt) -> Iterator[str]:
        """Execute a prompt, yielding content chunks as they are produced."""
        ...
