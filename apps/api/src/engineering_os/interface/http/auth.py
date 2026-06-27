"""Authentication endpoints — GitHub OAuth login, callback, current user, logout.

This router *is* the application boundary. It turns a GitHub identity into a session and a cookie;
downstream the compiler only ever sees a Project. Authentication wraps the compiler — it is not a
compiler pass (ADR-0012)."""
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from ...config import settings
from ...modules.identity.service import IdentityService
from ...ports.oauth import OAuthProvider
from .deps import get_current_user, get_db, get_oauth_provider
from .schemas import UserOut

router = APIRouter(prefix="/api/v1/auth")

_STATE_COOKIE = "eos_oauth_state"


def _set_cookie(resp: Response, key: str, value: str, max_age: int) -> None:
    resp.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )


@router.get("/github/login")
def github_login(oauth: OAuthProvider = Depends(get_oauth_provider)) -> RedirectResponse:
    """Begin the OAuth dance: mint an anti-CSRF state, stash it in a cookie, and redirect to GitHub."""
    state = secrets.token_urlsafe(16)
    resp = RedirectResponse(url=oauth.authorize_url(state), status_code=307)
    _set_cookie(resp, _STATE_COOKIE, state, max_age=600)
    return resp


@router.get("/github/callback")
def github_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
    oauth: OAuthProvider = Depends(get_oauth_provider),
) -> RedirectResponse:
    """Complete OAuth: verify state, exchange the code, resolve the identity, mint a session."""
    expected = request.cookies.get(_STATE_COOKIE, "")
    if not expected or not secrets.compare_digest(expected, state):
        raise HTTPException(status_code=400, detail="invalid OAuth state")

    token = oauth.exchange_code(code)
    identity = oauth.fetch_identity(token)

    identities = IdentityService(db)
    user = identities.upsert_user(identity)
    session = identities.create_session(user.id, token)

    resp = RedirectResponse(url=settings.web_url, status_code=307)
    _set_cookie(resp, settings.session_cookie, session.id, max_age=60 * 60 * 24 * 14)
    resp.delete_cookie(_STATE_COOKIE, path="/")
    return resp


@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)) -> UserOut:
    return UserOut(id=user.id, username=user.username, avatar_url=user.avatar_url, created_at=user.created_at)


@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)) -> Response:
    session_id = request.cookies.get(settings.session_cookie, "")
    IdentityService(db).delete_session(session_id)
    resp = JSONResponse({"status": "logged out"})
    resp.delete_cookie(settings.session_cookie, path="/")
    return resp
