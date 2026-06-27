"""Dependency-driven execution (v1.0-α2, ADR-0017). The compiler no longer runs a pipeline — it runs
only the work the dependency graph implies. The headline property: change one input, and only the
passes transitively downstream of it execute; everything else is reused."""
from engineering_os.modules.compiler.cache import InMemoryPassCache
from engineering_os.modules.compiler.context import ContextKey
from engineering_os.modules.compiler.passes import (
    EXPLAIN_PIPELINE,
    IDEA,
    SOURCES,
    TITLE,
    Compiler,
    PassDescriptor,
)

# A synthetic pipeline with two independent branches, so a change can be isolated:
#   A: TITLE -> X        B: IDEA -> Y        C: X -> Z   (C depends on A only)
X = ContextKey("x", str)
Y = ContextKey("y", str)
Z = ContextKey("z", str)


class PassA:
    descriptor = PassDescriptor("a", 1, (TITLE,), (X,), True, True)

    def run(self, ctx):
        return {X: ctx.get(TITLE).upper()}


class PassB:
    descriptor = PassDescriptor("b", 1, (IDEA,), (Y,), True, True)

    def run(self, ctx):
        return {Y: ctx.get(IDEA).upper()}


class PassC:
    descriptor = PassDescriptor("c", 1, (X,), (Z,), True, True)

    def run(self, ctx):
        return {Z: ctx.get(X) + "!"}


BRANCHED = (PassA(), PassB(), PassC())
SEED_KEYS = (TITLE, IDEA)


def _compiler():
    return Compiler(BRANCHED, seed_keys=SEED_KEYS, cache=InMemoryPassCache())


def test_warm_plan_reuses_everything():
    c = _compiler()
    seed = {TITLE: "app", IDEA: "an idea"}
    c.run(seed)                                   # cold: primes the cache
    plan = c.plan(seed)                           # warm: predict
    assert plan.required == [] and set(plan.reused) == {"a", "b", "c"}


def test_changing_one_input_executes_only_its_subgraph():
    c = _compiler()
    c.run({TITLE: "app", IDEA: "an idea"})        # prime cache
    # Only IDEA changed → only B depends on IDEA. A (TITLE) and C (depends on A) are untouched.
    plan = c.plan({TITLE: "app", IDEA: "a different idea"})
    assert plan.required == ["b"]
    assert set(plan.reused) == {"a", "c"}


def test_change_propagates_to_dependents():
    c = _compiler()
    c.run({TITLE: "app", IDEA: "an idea"})        # prime cache
    # TITLE changed → A re-executes, and C consumes A's output, so C must re-execute too. B is reused.
    plan = c.plan({TITLE: "renamed", IDEA: "an idea"})
    assert plan.required == ["a", "c"]
    assert plan.reused == ["b"]


def test_run_executes_only_required_passes():
    c = _compiler()
    seed = {TITLE: "app", IDEA: "an idea"}
    c.run(seed)
    result = c.run({TITLE: "app", IDEA: "changed"})
    executed = [p.pass_id for p in result.report.passes_executed if not p.cache_hit]
    assert executed == result.plan.required == ["b"]


def test_plan_is_predictive_and_side_effect_free():
    c = _compiler()
    seed = {TITLE: "app", IDEA: "an idea"}
    c.run(seed)
    cache = c._cache
    hits, misses = cache.hits, cache.misses
    c.plan(seed)                                  # planning peeks; it must not touch hit/miss stats
    c.plan(seed)
    assert (cache.hits, cache.misses) == (hits, misses)


def test_explain_pipeline_full_subgraph_on_cold_build():
    plan = Compiler(EXPLAIN_PIPELINE, cache=InMemoryPassCache()).plan(
        {TITLE: "App", IDEA: "a FastAPI app", SOURCES: {"vision": "# V\n## Problem\nx\n"}}
    )
    # Nothing cached yet → the whole pipeline is required, in topological order.
    assert plan.required == ["extract_knowledge", "extract_decision", "build", "explain"]
    assert plan.reused == []
