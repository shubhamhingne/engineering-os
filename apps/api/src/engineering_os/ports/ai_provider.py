"""The AI provider port. The application core depends on this, never on a vendor SDK."""
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class GenerationResult:
    content: str
    model: str
    tokens_in: int = 0
    tokens_out: int = 0


@runtime_checkable
class AIProvider(Protocol):
    name: str

    def generate_vision(self, idea: str) -> GenerationResult:
        """Generate a product Vision (Markdown) from a one-line idea."""
        ...
