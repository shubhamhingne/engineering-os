"""Request/response models — the HTTP boundary contract (artifact-centric)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserOut(BaseModel):
    id: str
    username: str
    avatar_url: Optional[str] = None
    created_at: datetime


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    idea: str = Field(min_length=1)


class ArtifactSave(BaseModel):
    content: str = Field(min_length=1)


class ArtifactVersionOut(BaseModel):
    type: str
    version: int
    source: str
    content: str
    model: Optional[str] = None
    created_at: datetime


class VersionSummaryOut(BaseModel):
    version: int
    source: str
    model: Optional[str] = None
    created_at: datetime


class ProjectOut(BaseModel):
    id: str
    title: str
    idea: str
    artifact_types: list[str] = []
    created_at: datetime
    updated_at: datetime


class ReadmeQualityOut(BaseModel):
    score: int
    missing: list[str]
    provenance: dict[str, list[str]]


class PublishRequest(BaseModel):
    repo_name: str = Field(min_length=1, max_length=100)
    private: bool = False


class PublishResultOut(BaseModel):
    target: str
    url: Optional[str] = None
    commit_sha: Optional[str] = None
    size_bytes: int
    artifact_count: int


class ExportJobOut(BaseModel):
    id: str
    status: str
    filename: str
    size_bytes: int
    artifact_count: int
    created_at: datetime


class ExplanationOut(BaseModel):
    entity_id: str
    type: str
    label: str
    summary: str
    evidence: list[str]
    sources: list[str]
    appears_in: list[str]
    related_decisions: list[str]
    confidence: float


class BuildPlanItemOut(BaseModel):
    renderer: str
    build: bool
    reason: str


class BuildPlanOut(BaseModel):
    items: list[BuildPlanItemOut]


class BundleDiffOut(BaseModel):
    added: list[str]
    changed: list[str]
    unchanged: list[str]
    removed: list[str]
    has_changes: bool
