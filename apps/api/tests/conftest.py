import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from engineering_os.adapters.ai.fake import FakeAIProvider
from engineering_os.adapters.db import models  # noqa: F401  (register tables on Base)
from engineering_os.adapters.db.models import User
from engineering_os.adapters.oauth.github import FakeOAuthProvider
from engineering_os.db import Base
from engineering_os.interface.http.deps import (
    get_current_user,
    get_db,
    get_oauth_provider,
    get_provider,
)
from engineering_os.main import app

# A fixed identity the authenticated `client` fixture acts as, so existing project-scoped tests
# (which predate auth) keep exercising the real ownership path with a known owner.
TEST_USER_ID = "test-user-1"


def _test_user() -> User:
    return User(
        id=TEST_USER_ID,
        github_id="gh_tester",
        username="tester",
        avatar_url=None,
        created_at=dt.datetime.now(dt.timezone.utc),
    )


@pytest.fixture
def session_factory():
    # StaticPool keeps a single in-memory connection so data persists across sessions.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False)
    # Seed the test user so the real auth path (anon_client) and FK-backed rows are consistent.
    seed = factory()
    seed.add(_test_user())
    seed.commit()
    seed.close()
    return factory


@pytest.fixture
def db(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def _override_db_factory(session_factory):
    def _override_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    return _override_db


@pytest.fixture
def client(session_factory):
    """Authenticated client — acts as TEST_USER_ID. Authorization (ownership) is still enforced;
    only authentication is stubbed, so project-scoped tests run against the real owned-project path."""
    app.dependency_overrides[get_db] = _override_db_factory(session_factory)
    app.dependency_overrides[get_provider] = lambda: FakeAIProvider()
    app.dependency_overrides[get_current_user] = _test_user
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def anon_client(session_factory):
    """Unauthenticated client wired to the fake OAuth provider — for exercising the real login/
    callback/session flow and the 401/403 boundaries end to end."""
    app.dependency_overrides[get_db] = _override_db_factory(session_factory)
    app.dependency_overrides[get_provider] = lambda: FakeAIProvider()
    app.dependency_overrides[get_oauth_provider] = lambda: FakeOAuthProvider()
    yield TestClient(app)
    app.dependency_overrides.clear()
