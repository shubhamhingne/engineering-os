"""Database engine, session, and base. Persistence is an adapter behind the modules."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    # Import models so they register on Base before create_all.
    from .adapters.db import models  # noqa: F401

    Base.metadata.create_all(engine)
