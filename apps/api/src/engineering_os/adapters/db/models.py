"""SQLAlchemy models — generalized from VisionArtifact to a typed Artifact with immutable
version history (ADR-0004). This is the architecture's artifact-centric domain, realized."""
import datetime as dt
import enum
import uuid
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...db import Base


class ArtifactType(str, enum.Enum):
    VISION = "vision"
    PRD = "prd"
    README = "readme"
    ADR = "adr"


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class User(Base):
    """An authenticated identity. GitHub is the only federation today (Alpha-0.8), so the identity
    is intentionally minimal — no passwords, no profile. The application layer owns this model; the
    compiler never sees it (ADR-0012)."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    github_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(120))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(400), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class UserSession(Base):
    """An application session: the bridge between a logged-in user and the GitHub access token used
    for publishing. The token lives here, scoped to the session — never on the User, never in the
    compiler. The opaque `id` is the cookie value."""

    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    github_token: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    owner_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    idea: Mapped[str] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    artifacts: Mapped[list["Artifact"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    export_jobs: Mapped[list["ExportJob"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Artifact(Base):
    """One artifact per (project, type). Its history lives in append-only versions."""

    __tablename__ = "artifacts"
    __table_args__ = (UniqueConstraint("project_id", "type", name="uq_artifact_project_type"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    type: Mapped[str] = mapped_column(String(20))  # ArtifactType value
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    project: Mapped[Project] = relationship(back_populates="artifacts")
    versions: Mapped[list["ArtifactVersion"]] = relationship(
        back_populates="artifact",
        cascade="all, delete-orphan",
        order_by="ArtifactVersion.version_no",
    )


class ArtifactVersion(Base):
    """Immutable revision. Editing creates a new version; nothing is overwritten (Principle 3)."""

    __tablename__ = "artifact_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.id"))
    version_no: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(10))  # "ai" | "human"
    model: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    artifact: Mapped[Artifact] = relationship(back_populates="versions")


class ExportJob(Base):
    """An observable export of a project to a packaged artifact (a ZIP for now). Modeled as a
    job, not a one-shot call, so the pipeline can grow (GitHub push, more outputs) — ADR-0006."""

    __tablename__ = "export_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    status: Mapped[str] = mapped_column(String(20))  # completed | failed
    filename: Mapped[str] = mapped_column(String(160))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    artifact_count: Mapped[int] = mapped_column(Integer, default=0)
    zip_data: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    project: Mapped[Project] = relationship(back_populates="export_jobs")

