"""Deterministic provider for tests and offline development. Type-aware so PRD and Vision
outputs are distinguishable without a network or key."""
from ...ports.ai_provider import GenerationResult, Prompt


class FakeAIProvider:
    name = "fake"

    def generate(self, prompt: Prompt) -> GenerationResult:
        last_line = prompt.user.strip().splitlines()[-1] if prompt.user.strip() else ""
        if prompt.artifact_type == "prd":
            content = (
                "# Product Requirements Document\n\n"
                "## Overview\nDerived from the project Vision.\n\n"
                "## Goals\n- Prove the core loop end to end.\n\n"
                "## Non-goals\n- Everything not required for the MVP.\n\n"
                "## Requirements\n- The system generates and persists this PRD as a versioned artifact.\n\n"
                "## Risks\n- Scope creep; mitigated by a hard MVP boundary.\n"
            )
        else:  # vision (default)
            content = (
                "# Product Vision\n\n"
                "## Problem\n"
                f"{last_line}\n\n"
                "## Vision\nA focused product solved through one clear, opinionated workflow.\n\n"
                "## Why now\nThe enabling tools have matured enough to make this practical.\n\n"
                "## What success looks like\nUsers accomplish the core job faster and with confidence.\n"
            )
        return GenerationResult(
            content=content,
            model="fake-1",
            tokens_in=len(prompt.user.split()),
            tokens_out=len(content.split()),
        )
