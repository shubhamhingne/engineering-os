"""Performance budgets — regression guards, not microbenchmarks. Thresholds are deliberately generous
so they catch catastrophic slowdowns without flaking on a busy CI box."""
import time

from engineering_os.modules.compiler.cache import InMemoryPassCache
from engineering_os.modules.compiler.passes import (
    EXPLAIN_PIPELINE,
    IDEA,
    SOURCES,
    TITLE,
    Compiler,
    compile_project,
)

SOURCES_FIXTURE = {"vision": "# V\n\n## Problem\nneeds authentication\n"}


def test_single_compile_within_budget():
    start = time.perf_counter()
    compile_project("App", "a FastAPI app with authentication", SOURCES_FIXTURE)
    assert (time.perf_counter() - start) < 1.0          # a full compile is milliseconds; guard at 1s


def test_compile_throughput_within_budget():
    start = time.perf_counter()
    for _ in range(20):
        compile_project("App", "a FastAPI app", SOURCES_FIXTURE)
    assert (time.perf_counter() - start) < 5.0          # < 250ms each — very safe


def test_caching_engages_on_recompile():
    cache = InMemoryPassCache()
    compiler = Compiler(EXPLAIN_PIPELINE, cache=cache)
    seed = {TITLE: "App", IDEA: "a FastAPI app", SOURCES: SOURCES_FIXTURE}
    compiler.run(seed)
    warm = compiler.run(seed)
    assert warm.report.cache_hits == len(EXPLAIN_PIPELINE)   # recompile reuses every pass
