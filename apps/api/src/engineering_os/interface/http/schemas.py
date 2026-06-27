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


class BuildManifestOut(BaseModel):
    manifest_hash: str
    compiler_fingerprint: str
    plan_id: str
    report_id: str
    repository_state_id: Optional[str] = None
    artifact_hashes: dict[str, str]
    generated_at: Optional[str] = None


class PassResultOut(BaseModel):
    pass_id: str
    duration_ms: int
    cache_hit: bool
    inputs: list[str]
    outputs: list[str]
    input_hash: str
    output_hash: str
    invalidation_reason: str
    warnings: list[str]
    errors: list[str]


class CompilationReportOut(BaseModel):
    compiler_version: str
    fingerprint: str
    schema_versions: dict[str, str]
    passes_executed: list[PassResultOut]
    artifacts_generated: int
    artifacts_reused: int
    cache_hits: int
    warnings: list[str]
    duration_ms: int
    commit_sha: Optional[str] = None


class PipelineEdgeOut(BaseModel):
    producer: str
    consumer: str


class CompilerPipelineOut(BaseModel):
    fingerprint: str
    compiler_version: str
    nodes: list[str]
    edges: list[PipelineEdgeOut]
    mermaid: str
    cycle: Optional[list[str]] = None
    unreachable: list[str]


class RepositoryStateOut(BaseModel):
    repository: str
    default_branch: str
    published_commit: Optional[str] = None
    remote_artifact_hashes: dict[str, str]
    sync_status: str
    pending_artifacts: list[str]
    last_sync: Optional[str] = None
    remote_fingerprint: Optional[str] = None
    diagnostics: list[str]


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
