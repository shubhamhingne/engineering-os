"""Compiler hardening (v1.0-α4, ADR-0019). Property-based and adversarial tests that try to break
the invariants under randomly generated pipelines — the difference between claiming this is a
compiler and proving it. Synthetic passes (str-valued slots) let Hypothesis generate arbitrary
acyclic dependency graphs over two independent seed inputs."""
import json

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from engineering_os.modules.compiler.cache import InMemoryPassCache
from engineering_os.modules.compiler.context import ContextKey
from engineering_os.modules.compiler.graph import build_dependency_graph
from engineering_os.modules.compiler.manifest import build_manifest
from engineering_os.modules.compiler.passes import (
    Compiler,
    PassDescriptor,
    PipelineValidationError,
    compile_project,
    compute_fingerprint,
)

SEED_A = ContextKey("seed_a", str)
SEED_B = ContextKey("seed_b", str)
SEEDS = (SEED_A, SEED_B)
SETTINGS = settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])


def _make_pass(pid, produces, consumes, version=1, cacheable=True, deterministic=True):
    descriptor = PassDescriptor(pid, version, tuple(consumes), (produces,), deterministic, cacheable)

    class _SyntheticPass:
        pass

    _SyntheticPass.descriptor = descriptor

    def run(self, ctx, _c=tuple(consumes), _p=produces, _id=pid):
        return {_p: _id + "(" + ",".join(ctx.get(k) for k in _c) + ")"}

    _SyntheticPass.run = run
    return _SyntheticPass()


@st.composite
def pipelines(draw, max_nodes=6):
    """A random valid pipeline: node i may consume the two seeds and any earlier node's output, so the
    listed order is always a valid topological order and every slot has exactly one producer."""
    n = draw(st.integers(min_value=1, max_value=max_nodes))
    keys = [ContextKey(f"k{i}", str) for i in range(n)]
    passes = []
    for i in range(n):
        candidates = list(SEEDS) + keys[:i]
        consumes = draw(
            st.lists(st.sampled_from(candidates), unique_by=lambda k: k.name, min_size=1, max_size=len(candidates))
        )
        passes.append(_make_pass(f"p{i}", keys[i], consumes))
    return passes, keys


# 1. DAG correctness ------------------------------------------------------------------------------

@given(pipelines())
@SETTINGS
def test_random_valid_dag_validates_executes_and_serializes_stably(data):
    passes, keys = data
    Compiler(passes, seed_keys=SEEDS)                       # validates without raising
    dag = build_dependency_graph(passes, SEEDS)
    assert dag.find_cycle() is None
    once = json.dumps([list(e) for e in dag.edges], sort_keys=True)
    twice = json.dumps([list(e) for e in build_dependency_graph(passes, SEEDS).edges], sort_keys=True)
    assert once == twice                                   # graph identical after serialization
    result = Compiler(passes, seed_keys=SEEDS).run({SEED_A: "a", SEED_B: "b"})
    for k in keys:                                         # topological execution satisfied every dependency
        assert result.context.has(k)


# 2. Cycle / back-edge detection -------------------------------------------------------------------

@given(pipelines(max_nodes=5))
@SETTINGS
def test_a_back_edge_is_always_rejected_at_startup(data):
    passes, keys = data
    assume(len(passes) >= 2)
    # Make the first pass consume the last pass's output — a back edge relative to topological order.
    d = passes[0].descriptor
    broken = [_make_pass(d.id, d.produces[0], tuple(d.consumes) + (keys[-1],))] + passes[1:]
    with pytest.raises(PipelineValidationError):
        Compiler(broken, seed_keys=SEEDS)


def test_two_node_cycle_is_detected():
    a = ContextKey("a", str)
    b = ContextKey("b", str)
    pa = _make_pass("pa", a, (b,))   # pa consumes b
    pb = _make_pass("pb", b, (a,))   # pb consumes a  → a↔b cycle
    assert build_dependency_graph([pa, pb], ()).find_cycle() is not None
    with pytest.raises(PipelineValidationError):
        Compiler([pa, pb], seed_keys=())


# 3. Manifest identity: equivalent artifacts ⇒ equivalent manifest (invariant: Identity) -----------

@given(pipelines())
@SETTINGS
def test_manifest_hash_is_execution_independent(data):
    passes, _keys = data
    compiler = Compiler(passes, seed_keys=SEEDS, cache=InMemoryPassCache())
    seed = {SEED_A: "a", SEED_B: "b"}
    cold = build_manifest(compiler.run(seed))              # all required
    warm = build_manifest(compiler.run(seed))              # all reused
    assert cold.manifest_hash == warm.manifest_hash        # same WHAT, regardless of HOW


# 4. Fingerprint stability and sensitivity ---------------------------------------------------------

@given(pipelines())
@SETTINGS
def test_fingerprint_is_stable_then_sensitive_to_a_version_bump(data):
    passes, _keys = data
    fingerprint = compute_fingerprint(passes, SEEDS)
    assert fingerprint == compute_fingerprint(passes, SEEDS)            # stable
    d = passes[0].descriptor
    perturbed = [_make_pass(d.id, d.produces[0], tuple(d.consumes), version=d.version + 1)] + passes[1:]
    assert compute_fingerprint(perturbed, SEEDS) != fingerprint         # a version bump changes it


# 5. Cache correctness: execute → cache → reuse → identical ----------------------------------------

@given(pipelines())
@SETTINGS
def test_cache_reuse_preserves_every_output(data):
    passes, keys = data
    compiler = Compiler(passes, seed_keys=SEEDS, cache=InMemoryPassCache())
    seed = {SEED_A: "a", SEED_B: "b"}
    first = compiler.run(seed)
    second = compiler.run(seed)
    for k in keys:
        assert first.context.get(k) == second.context.get(k)
    assert all(p.cache_hit for p in second.report.passes_executed)      # warm run reused everything


# 6. Dependency pruning: only the forward closure of a changed input re-executes -------------------

@given(pipelines())
@SETTINGS
def test_changing_one_input_requires_exactly_its_forward_closure(data):
    passes, _keys = data
    compiler = Compiler(passes, seed_keys=SEEDS, cache=InMemoryPassCache())
    compiler.run({SEED_A: "a", SEED_B: "b"})               # prime the cache
    plan = compiler.plan({SEED_A: "CHANGED", SEED_B: "b"})  # only seed_a changed

    # Expected required set = forward closure of seed_a through the consume edges (the planner's rule).
    dirty = {SEED_A.name}
    expected = []
    for p in passes:
        d = p.descriptor
        if any(c.name in dirty for c in d.consumes):
            expected.append(d.id)
            dirty.add(d.produces[0].name)

    assert plan.required == expected
    assert set(plan.reused) == ({p.descriptor.id for p in passes} - set(expected))


# Replay identity (not property-based): the receipt is sufficient to identify the build -----------

def test_manifest_replay_reproduces_identity():
    inputs = ("App", "a FastAPI app with authentication", {"vision": "# V\n\n## Problem\nx\n"})
    original = build_manifest(compile_project(*inputs))
    replayed = build_manifest(compile_project(*inputs))    # reconstruct from the same build
    assert replayed.manifest_hash == original.manifest_hash
    assert replayed.artifact_hashes == original.artifact_hashes
