"""FastAPI dependencies — wiring adapters to the core at the edge (composition root).

This is where the application boundary lives: authentication and authorization happen here, in
front of the compiler. The compiler-facing services receive a Project; they never receive a User,
a session, or a token (ADR-0012)."""
from collections.abc import Iterator

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ...adapters.ai.fake import FakeAIProvider
from ...adapters.db.models import Project, User
from ...config import settings
from ...db import SessionLocal
from ...modules.identity.credentials import GitHubCredentialProvider
from ...modules.identity.service import IdentityService
from ...modules.projects.service import NotFoundError, ProjectService
from ...ports.ai_provider import AIProvider
from ...ports.credentials import CredentialProvider, MissingCredentialError
from ...ports.oauth import OAuthProvider


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


def get_oauth_provider() -> OAuthProvider:
    """Real GitHub OAuth when configured; otherwise a deterministic fake (no GitHub app needed)."""
    from ...adapters.oauth.github import FakeOAuthProvider, GitHubOAuthProvider

    if settings.github_oauth_client_id and settings.github_oauth_client_secret:
        return GitHubOAuthProvider(
            settings.github_oauth_client_id, settings.github_oauth_client_secret, settings.oauth_redirect_uri
        )
    return FakeOAuthProvider()


# --- Authentication & authorization (the application boundary) ------------------------------------

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Resolve the session cookie to a User, or 401. Everything project-scoped depends on this."""
    session_id = request.cookies.get(settings.session_cookie, "")
    session = IdentityService(db).get_session(session_id)
    if session is None:
        raise HTTPException(status_code=401, detail="authentication required")
    user = db.get(User, session.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid session")
    # Stash the session so credential resolution doesn't re-read the cookie.
    request.state.session = session
    return user


def get_owned_project(
    project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Project:
    """Authorization in one place: the project must exist (404) and be owned by the caller (403)."""
    try:
        project = ProjectService(db).get(project_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="project not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="you do not own this project")
    return project


def get_credential_provider(
    request: Request, user: User = Depends(get_current_user)
) -> CredentialProvider:
    """The session's GitHub token, wrapped as a CredentialProvider. Depends on get_current_user so
    the session is already resolved and authenticated."""
    session = request.state.session
    return GitHubCredentialProvider(session.github_token)


def get_github_client(credentials: CredentialProvider = Depends(get_credential_provider)):
    """Build the GitHub API client from the session credential — the publisher never sees OAuth.
    Returns None when no credential is available, so the endpoint can answer 400 cleanly."""
    try:
        token = credentials.get_publishing_credential("github")
    except MissingCredentialError:
        return None
    from ...modules.publish.github import RealGitHubClient

    return RealGitHubClient(token)


def get_repository_reader(credentials: CredentialProvider = Depends(get_credential_provider)):
    """Build the read-only remote reader from the session credential. The reader carries the token,
    so `RepositorySyncPass` receives a capability, not OAuth — the compiler still never sees identity.
    Returns None when no credential is available."""
    try:
        token = credentials.get_publishing_credential("github")
    except MissingCredentialError:
        return None
    from ...adapters.repository.github import GitHubRepositoryReader

    return GitHubRepositoryReader(token)
