"""FastAPI dependencies — wiring adapters to the core at the edge (composition root)."""
from collections.abc import Iterator

from sqlalchemy.orm import Session

from ...adapters.ai.fake import FakeAIProvider
from ...config import settings
from ...db import SessionLocal
from ...ports.ai_provider import AIProvider


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_provider() -> AIProvider:
    if settings.ai_provider == "anthropic" and settings.anthropic_api_key:
        from ...adapters.ai.anthropic import AnthropicProvider

        return AnthropicProvider(settings.anthropic_api_key, settings.ai_model)
    return FakeAIProvider()


def get_github_client():
    """The real GitHub client when a token is configured; otherwise None (tests inject a fake)."""
    if settings.github_token:
        from ...modules.publish.github import RealGitHubClient

        return RealGitHubClient(settings.github_token)
    return None
