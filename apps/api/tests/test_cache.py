"""Pass-output caching (v1.0, ADR-0016). The cache turns the metadata the compiler already collects
— pass id, pass version, input hash, fingerprint — into reuse. Injected at the boundary, so default
runs stay cache-less and deterministic."""
from engineering_os.adapters.repository.github import FakeRepositoryReader
from engineering_os.modules.compiler.cache import InMemoryPassCache
from engineering_os.modules.compiler.passes import (
    EXPLAIN_PIPELINE,
    IDEA,
    SOURCES,
    TITLE,
    BuildPass,
    Compiler,
    RepositorySyncPass,
)

SEED = {TITLE: "App", IDEA: "a FastAPI app with authentication",
        SOURCES: {"vision": "# V\n\n## Problem\nneeds authentication\n"}}


def test_cold_run_misses_then_warm_run_hits():
    cache = InMemoryPassCache()
    compiler = Compiler(EXPLAIN_PIPELINE, cache=cache)

    cold = compiler.run(SEED).report
    assert cold.cache_hits == 0
    assert cold.artifacts_generated > 0 and cold.artifacts_reused == 0

    warm = compiler.run(SEED).report
    assert warm.cache_hits == len(EXPLAIN_PIPELINE)            # every cacheable pass reused
    assert warm.artifacts_generated == 0 and warm.artifacts_reused == cold.artifacts_generated
    assert all(p.invalidation_reason == "cache hit" for p in warm.passes_executed)


def test_changed_inputs_invalidate_the_cache():
    cache = InMemoryPassCache()
    compiler = Compiler(EXPLAIN_PIPELINE, cache=cache)
    compiler.run(SEED)
    changed = compiler.run({**SEED, IDEA: "a FastAPI app with billing"}).report
    assert changed.cache_hits == 0                            # different input_hash → different key


def test_default_compiler_is_cache_less_and_deterministic():
    # No cache injected → every run is a cold build (existing behavior is preserved).
    report = Compiler(EXPLAIN_PIPELINE).run(SEED).report
    assert report.cache_hits == 0
    assert all("cache hit" not in p.invalidation_reason for p in report.passes_executed)


def test_non_cacheable_pass_is_never_cached():
    # RepositorySyncPass reads live remote state, so it must re-run every time even with a warm cache.
    cache = InMemoryPassCache()
    compiler = Compiler((BuildPass(), RepositorySyncPass(FakeRepositoryReader(None), "o/a")), cache=cache)
    compiler.run(SEED)
    warm = compiler.run(SEED).report
    by_id = {p.pass_id: p for p in warm.passes_executed}
    assert by_id["build"].cache_hit is True                   # cacheable → reused
    assert by_id["repository_sync"].cache_hit is False        # not cacheable → always observes live


def test_cache_key_binds_version_input_and_fingerprint():
    from engineering_os.modules.compiler.passes import ExtractKnowledgePass, PassDescriptor, _cache_key

    d = ExtractKnowledgePass.descriptor
    base = _cache_key(d, "inhash", "fp")
    bumped = PassDescriptor(d.id, d.version + 1, d.consumes, d.produces, d.deterministic, d.cacheable)
    assert _cache_key(d, "inhash", "fp") == base              # stable
    assert _cache_key(bumped, "inhash", "fp") != base         # pass version is part of the key
    assert _cache_key(d, "other", "fp") != base               # input hash is part of the key
    assert _cache_key(d, "inhash", "fp2") != base             # compiler fingerprint is part of the key
