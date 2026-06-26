"""SQLAlchemy models. Persistence adapter for the Projects module."""
import datetime as dt
import uuid
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(200))
    idea: Mapped[str] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    vision: Mapped[Optional["VisionArtifact"]] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan"
    )


class VisionArtifact(Base):
    """One Vision per project for the slice. `version` increments on edit and `source`
    records provenance (ai|human). The documented architecture uses immutable versions;
    the slice keeps the current version + a counter, which is forward-compatible."""

    __tablename__ = "vision_artifacts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), unique=True)
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(10))  # "ai" | "human"
    version: Mapped[int] = mapped_column(Integer, default=1)
    model: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    project: Mapped[Project] = relationship(back_populates="vision")
