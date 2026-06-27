"""Identity module — users and sessions. Lives in the application layer, alongside (not inside)
the compiler. It turns an OAuth identity into a persistent User and mints the session that carries
the GitHub token (ADR-0012)."""
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional

from ...adapters.db.models import User, UserSession
from ...ports.oauth import OAuthIdentity
from .crypto import TokenCipher, get_token_cipher


class IdentityService:
    def __init__(self, db: Session, cipher: Optional[TokenCipher] = None) -> None:
        self._db = db
        self._cipher = cipher or get_token_cipher()

    def upsert_user(self, identity: OAuthIdentity) -> User:
        """Find-or-create by GitHub id, refreshing the mutable profile fields on each login."""
        user = self._db.scalar(select(User).where(User.github_id == identity.github_id))
        if user is None:
            user = User(github_id=identity.github_id, username=identity.username, avatar_url=identity.avatar_url)
            self._db.add(user)
        else:
            user.username = identity.username
            user.avatar_url = identity.avatar_url
        self._db.commit()
        self._db.refresh(user)
        return user

    def create_session(self, user_id: str, github_token: str) -> UserSession:
        # The token is encrypted before it touches the column; it is never stored as plaintext (BR-02).
        session = UserSession(
            id=secrets.token_urlsafe(32),
            user_id=user_id,
            github_token=self._cipher.encrypt(github_token),
        )
        self._db.add(session)
        self._db.commit()
        self._db.refresh(session)
        return session

    def decrypt_token(self, session: UserSession) -> str:
        """Recover the plaintext token at the point of use (never stored decrypted)."""
        return self._cipher.decrypt(session.github_token)

    def get_session(self, session_id: str) -> Optional[UserSession]:
        if not session_id:
            return None
        return self._db.get(UserSession, session_id)

    def delete_session(self, session_id: str) -> None:
        session = self._db.get(UserSession, session_id)
        if session is not None:
            self._db.delete(session)
            self._db.commit()
