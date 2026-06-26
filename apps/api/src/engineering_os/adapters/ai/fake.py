"""Deterministic provider for tests and offline development. Type-aware, and streams in chunks
so the streaming pipeline is testable without a network or key."""
from collections.abc import Iterator

from ...ports.ai_provider import GenerationResult, Prompt


def _content_for(prompt: Prompt) -> str:
    last_line = prompt.user.strip().splitlines()[-1] if prompt.user.strip() else ""
    if prompt.artifact_type == "prd":
        return (
            "# Product Requirements Document\n\n"
            "## Overview\nDerived from the project Vision.\n\n"
            "## Goals\n- Prove the core loop end to end.\n\n"
            "## Non-goals\n- Everything not required for the MVP.\n\n"
            "## Requirements\n- The system generates and persists this PRD as a versioned artifact.\n\n"
            "## Risks\n- Scope creep; mitigated by a hard MVP boundary.\n"
        )
    return (
        "# Product Vision\n\n"
        "## Problem\n"
        f"{last_line}\n\n"
        "## Vision\nA focused product solved through one clear, opinionated workflow.\n\n"
        "## Why now\nThe enabling tools have matured enough to make this practical.\n\n"
        "## What success looks like\nUsers accomplish the core job faster and with confidence.\n"
    )


class FakeAIProvider:
    name = "fake"
    model = "fake-1"

    def generate(self, prompt: Prompt) -> GenerationResult:
        content = _content_for(prompt)
        return GenerationResult(
            content=content,
            model=self.model,
            tokens_in=len(prompt.user.split()),
            tokens_out=len(content.split()),
        )

    def stream(self, prompt: Prompt) -> Iterator[str]:
        content = _content_for(prompt)
        words = content.split(" ")
        step = max(1, len(words) // 8)
        for i in range(0, len(words), step):
            yield " ".join(words[i : i + step]) + " "
