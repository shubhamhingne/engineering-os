import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from engineering_os.adapters.ai.fake import FakeAIProvider
from engineering_os.adapters.db import models  # noqa: F401  (register tables on Base)
from engineering_os.db import Base
from engineering_os.interface.http.deps import get_db, get_provider
from engineering_os.main import app


@pytest.fixture
def session_factory():
    # StaticPool keeps a single in-memory connection so data persists across sessions.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False)


@pytest.fixture
def db(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(session_factory):
    def _override_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_provider] = lambda: FakeAIProvider()
    yield TestClient(app)
    app.dependency_overrides.clear()
