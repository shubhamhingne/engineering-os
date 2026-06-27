"""BuildManifest — the immutable receipt and identity of a compilation (v1.0-α3, ADR-0018).
Tiny, content-addressed, referencing the immutable products rather than duplicating them."""
import dataclasses

import pytest

from engineering_os.modules.compiler.cache import InMemoryPassCache
from engineering_os.modules.compiler.manifest import BuildManifest, build_manifest
from engineering_os.modules.compiler.passes import (
    EXPLAIN_PIPELINE,
    IDEA,
    SOURCES,
    TITLE,
    Compiler,
    compile_project,
)

SEED = {TITLE: "App", IDEA: "a FastAPI app with authentication",
        SOURCES: {"vision": "# V\n\n## Problem\nneeds authentication\n"}}


def test_manifest_references_products_without_duplicating_them():
    manifest = build_manifest(compile_project("App", "a FastAPI app", {"vision": "# V\n## Problem\nx\n"}))
    # It carries ids + artifact hashes — never a graph, report, or explanation.
    assert manifest.manifest_hash and manifest.compiler_fingerprint
    assert manifest.plan_id and manifest.report_id
    assert manifest.artifact_hashes
    fields = {f.name for f in dataclasses.fields(BuildManifest)}
    assert "knowledge" not in fields and "report" not in fields and "explanations" not in fields


def test_identical_inputs_share_a_manifest_hash():
    a = build_manifest(compile_project("App", "a FastAPI app", {"vision": "# V\n## Problem\nx\n"}))
    b = build_manifest(compile_project("App", "a FastAPI app", {"vision": "# V\n## Problem\nx\n"}))
    assert a.manifest_hash == b.manifest_hash


def test_different_inputs_produce_different_manifest_hashes():
    a = build_manifest(compile_project("App", "a FastAPI app with authentication", {"vision": "# V\nx\n"}))
    b = build_manifest(compile_project("App", "a FastAPI app with billing", {"vision": "# V\nx\n"}))
    assert a.manifest_hash != b.manifest_hash


def test_manifest_hash_is_execution_independent_cold_vs_warm():
    # Semantic identity: a cold build and a fully-cached rebuild of the same inputs produce the same
    # artifacts, so the same manifest hash — even though the execution (and so the plan id) differs.
    compiler = Compiler(EXPLAIN_PIPELINE, cache=InMemoryPassCache())
    cold = build_manifest(compiler.run(SEED))
    warm = build_manifest(compiler.run(SEED))
    assert cold.manifest_hash == warm.manifest_hash          # same WHAT
    assert cold.plan_id != warm.plan_id                       # different HOW (cold required, warm reused)


def test_manifest_is_immutable():
    manifest = build_manifest(compile_project("App", "a FastAPI app", {"vision": "# V\nx\n"}))
    with pytest.raises(dataclasses.FrozenInstanceError):
        manifest.manifest_hash = "tampered"


def test_build_manifest_endpoint(client):
    pid = client.post("/api/v1/projects", json={"title": "App", "idea": "a FastAPI app"}).json()["id"]
    client.post(f"/api/v1/projects/{pid}/artifacts/vision")
    data = client.get(f"/api/v1/projects/{pid}/build-manifest").json()
    assert data["manifest_hash"] and data["compiler_fingerprint"]
    assert data["plan_id"] and data["report_id"]
    assert data["artifact_hashes"]
