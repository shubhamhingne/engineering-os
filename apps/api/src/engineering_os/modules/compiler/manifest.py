"""BuildManifest — the immutable receipt and identity of one compilation (ADR-0018).

Intentionally tiny: it *references* the immutable products (plan, report, repository state) by id and
records the artifact hashes — it never duplicates a graph, report, or explanation. It answers one
question: "exactly what compilation are we talking about?"

`manifest_hash` is the compilation's *semantic identity*: a hash over the compiler fingerprint, the
artifact hashes, and the repository-state id — deliberately NOT over the plan/report ids. Those
encode *how* the result was produced (a cold build and a fully-cached rebuild of the same inputs run
differently but produce the same artifacts); the manifest hash captures *what* was produced. Same
manifest hash ⇔ same compiler made the same artifacts against the same remote state."""
import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Optional

from .passes import BUNDLE, REPOSITORY_STATE


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _identity(obj) -> str:
    """Content id of an immutable product — a hash over its full structure."""
    return _hash(json.dumps(asdict(obj), sort_keys=True, default=str))


@dataclass(frozen=True)
class BuildManifest:
    manifest_hash: str                       # the compilation's semantic identity (content-addressed)
    compiler_fingerprint: str
    plan_id: str                             # → locate the ExecutionPlan (navigation, not identity)
    report_id: str                           # → locate the CompilationReport
    repository_state_id: Optional[str]       # → locate the RepositoryState, if any
    artifact_hashes: dict
    generated_at: Optional[str] = None       # wall-clock metadata; NOT part of manifest_hash


def build_manifest(result, generated_at: Optional[str] = None) -> BuildManifest:
    ctx = result.context
    bundle = ctx.get(BUNDLE) if ctx.has(BUNDLE) else None
    artifact_hashes = {a.path: a.hash for a in bundle.artifacts} if bundle is not None else {}
    repository_state_id = _identity(ctx.get(REPOSITORY_STATE)) if ctx.has(REPOSITORY_STATE) else None

    semantic = {
        "fingerprint": result.report.fingerprint,
        "artifacts": sorted(artifact_hashes.items()),
        "repository_state_id": repository_state_id or "",
    }
    return BuildManifest(
        manifest_hash=_hash(json.dumps(semantic, sort_keys=True)),
        compiler_fingerprint=result.report.fingerprint,
        plan_id=_identity(result.plan) if result.plan is not None else "",
        report_id=_identity(result.report),
        repository_state_id=repository_state_id,
        artifact_hashes=artifact_hashes,
        generated_at=generated_at,
    )
