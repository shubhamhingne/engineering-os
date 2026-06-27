"""Explainability + the typed compiler (ADR-0011, ADR-0013). The ExplanationGraph is one output;
the CompilerContext symbol table, the startup validator, and the CompilationReport are the
machinery that produces it — provable, observable, and well-formed before it runs."""
import pytest

from engineering_os.modules.compiler.context import ContextKey
from engineering_os.modules.compiler.graph import build_dependency_graph
from engineering_os.modules.compiler.passes import (
    EXPLANATIONS,
    EXPLAIN_PIPELINE,
    SEED_KEYS,
    Compiler,
    ExtractDecisionPass,
    ExtractKnowledgePass,
    PipelineValidationError,
    compile_project,
    explain_compiler,
    run_explain_pipeline,
)


def test_every_pass_declares_a_typed_versioned_descriptor():
    for p in EXPLAIN_PIPELINE:
        d = p.descriptor
        assert isinstance(d.id, str) and d.id
        assert isinstance(d.version, int) and d.version >= 1
        assert all(isinstance(k, ContextKey) for k in d.consumes)
        assert all(isinstance(k, ContextKey) for k in d.produces)
        assert isinstance(d.deterministic, bool) and isinstance(d.cacheable, bool)
        if d.cacheable:  # you can't safely memoize a non-deterministic output
            assert d.deterministic


def test_fingerprint_is_stable_and_config_sensitive():
    base = explain_compiler().fingerprint
    assert base == explain_compiler().fingerprint                 # stable across calls
    # dropping a pass is a different compiler configuration → different fingerprint
    assert Compiler((ExtractKnowledgePass(),)).fingerprint != base


def test_dependency_graph_is_acyclic_and_fully_reachable():
    dag = build_dependency_graph(EXPLAIN_PIPELINE, SEED_KEYS)
    assert dag.find_cycle() is None
    assert dag.unreachable() == []
    assert ("extract_knowledge", "explain") in dag.edges


def test_validator_rejects_missing_producer():
    # extract_decision consumes `knowledge`, which nothing earlier produces.
    with pytest.raises(PipelineValidationError):
        Compiler((ExtractDecisionPass(),))


def test_validator_rejects_duplicate_producer():
    with pytest.raises(PipelineValidationError):
        Compiler((ExtractKnowledgePass(), ExtractKnowledgePass()))


def test_explain_pipeline_produces_explanations_with_provenance():
    sources = {
        "vision": "# V\n\n## Problem\nthe product needs authentication\n",
        "prd": "# P\n\n## Requirements\n- a FastAPI service\n",
    }
    graph = run_explain_pipeline("App", "a FastAPI app with authentication", sources)
    ids = {e.entity_id for e in graph.explanations}
    assert "topic:authentication" in ids and "tech:FastAPI" in ids

    auth = graph.get("topic:authentication")
    assert auth is not None
    assert auth.confidence > 0
    assert "vision" in auth.sources              # evidence: where it was mentioned
    assert any(p.endswith(".md") for p in auth.appears_in)  # provenance: produced artifacts


def test_compiler_records_an_execution_trace_and_report():
    result = compile_project(
        "App", "a FastAPI app with authentication", {"vision": "# V\n\n## Problem\nneeds authentication\n"}
    )
    report = result.report
    assert [p.pass_id for p in report.passes_executed] == [
        "extract_knowledge",
        "extract_decision",
        "build",
        "explain",
    ]
    assert report.artifacts_generated > 0
    assert report.fingerprint                     # the run records which compiler produced it
    # the report is versioned by every graph it touched (the build log of a semantic compile)
    assert report.schema_versions["knowledge"] == "v1"
    assert report.schema_versions["explanations"] == "v1"
    # every pass records why it ran and a hash of its inputs/outputs
    explain = next(p for p in report.passes_executed if p.pass_id == "explain")
    assert explain.input_hash and explain.output_hash
    assert "cold build" in explain.invalidation_reason
    # the explanations are still reachable as a typed slot in the symbol table
    assert result.context.get(EXPLANATIONS).explanations


def test_invalidation_reason_tracks_input_changes():
    src = {"vision": "# V\n\n## Problem\nneeds authentication\n"}
    first = compile_project("App", "a FastAPI app with authentication", src).report
    same = compile_project("App", "a FastAPI app with authentication", src, previous=first).report
    changed = compile_project("App", "a FastAPI app with authentication and billing", src, previous=first).report
    assert "unchanged" in same.passes_executed[0].invalidation_reason
    assert "changed" in changed.passes_executed[0].invalidation_reason


def test_explanations_endpoint(client):
    pid = client.post(
        "/api/v1/projects", json={"title": "App", "idea": "a FastAPI app with authentication"}
    ).json()["id"]
    client.post(f"/api/v1/projects/{pid}/artifacts/vision")
    data = client.get(f"/api/v1/projects/{pid}/explanations").json()
    ids = {e["entity_id"] for e in data}
    assert "topic:authentication" in ids and "tech:FastAPI" in ids
    auth = next(e for e in data if e["entity_id"] == "topic:authentication")
    assert auth["confidence"] > 0 and auth["appears_in"]


def test_compilation_report_endpoint(client):
    pid = client.post(
        "/api/v1/projects", json={"title": "App", "idea": "a FastAPI app with authentication"}
    ).json()["id"]
    client.post(f"/api/v1/projects/{pid}/artifacts/vision")
    report = client.get(f"/api/v1/projects/{pid}/compilation-report").json()
    assert report["compiler_version"]
    assert [p["pass_id"] for p in report["passes_executed"]] == [
        "extract_knowledge",
        "extract_decision",
        "build",
        "explain",
    ]
    assert report["artifacts_generated"] > 0
    assert report["fingerprint"]
    assert report["schema_versions"]["explanations"] == "v1"


def test_compiler_pipeline_endpoint(client):
    data = client.get("/api/v1/compiler/pipeline").json()
    assert data["fingerprint"] and data["compiler_version"]
    assert data["cycle"] is None and data["unreachable"] == []
    assert {"producer": "extract_knowledge", "consumer": "explain"} in data["edges"]
    assert data["mermaid"].startswith("graph TD")


def test_compiler_pipeline_requires_auth(anon_client):
    assert anon_client.get("/api/v1/compiler/pipeline").status_code == 401
