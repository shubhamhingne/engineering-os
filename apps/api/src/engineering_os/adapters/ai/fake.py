"""Deterministic provider for tests and offline development. No network, no key."""
from ...ports.ai_provider import GenerationResult


class FakeAIProvider:
    name = "fake"

    def generate_vision(self, idea: str) -> GenerationResult:
        idea = idea.strip()
        content = (
            "# Product Vision\n\n"
            "## Problem\n"
            f"{idea}\n\n"
            "## Vision\n"
            f'A focused product that addresses "{idea[:80]}" through one clear, '
            "opinionated workflow rather than a pile of features.\n\n"
            "## Why now\n"
            "The enabling tools have matured enough to make this practical today.\n\n"
            "## What success looks like\n"
            "Users accomplish the core job faster and with more confidence.\n"
        )
        return GenerationResult(
            content=content,
            model="fake-1",
            tokens_in=len(idea.split()),
            tokens_out=len(content.split()),
        )
