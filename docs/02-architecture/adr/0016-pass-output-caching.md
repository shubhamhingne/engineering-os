# 0016 — Pass-output caching

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0013](0013-typed-compiler-context.md), [ADR-0014](0014-compiler-fingerprint-and-dependency-graph.md), [ADR-0011](0011-explainability-compiler-passes.md)

## Context

The compiler already collected everything a cache needs — pass id, pass `version`, `input_hash`,
`cacheable`/`deterministic`, and the compiler `fingerprint` — but `cache_hit` and `artifacts_reused`
were inert (ADR-0014 shipped them as honest zeros). This is the first v1.0 step because it *activates
metadata already present* rather than introducing a new concept: it turns the bookkeeping into
observable reuse.

## Decision

Add a `PassCache` port (`get(key)` / `put(key, outputs)`) and an `InMemoryPassCache`. The cache key
binds four things:

```
cache_key = hash(pass_id, pass_version, input_hash, compiler_fingerprint)
```

In `Compiler.run`, for a pass that is `cacheable` (which, by invariant, implies `deterministic`):
a key hit replays the stored produced-slots into the context with `cache_hit=true` and
`invalidation_reason="cache hit"`, skipping execution; a miss runs the pass, stores its outputs, and
records `cache_hit=false`. Non-cacheable passes (e.g. `RepositorySyncPass`, which reads live remote
state) are never consulted or stored — they always execute. `artifacts_generated` vs
`artifacts_reused` now reflect whether the bundle came fresh or from cache.

**Injected at the boundary.** The cache is a constructor argument (`Compiler(passes, cache=…)`).
A long-lived worker or CLI opts in; per-request HTTP handlers stay **cache-less and deterministic**.
This is the same dependency-injection stance as every other adapter, and it avoids hidden
cross-request state in the API.

## Alternatives considered

- **A global, always-on cache inside the module singleton.** Rejected: it injects cross-request,
  cross-test statefulness and makes a per-request compile non-deterministic. Injection keeps control
  at the composition root.
- **Key on input hash alone.** Rejected: a pass-algorithm change (`version` bump) or a compiler-config
  change (fingerprint) must invalidate prior outputs — keying on all four is what makes reuse *safe*.
- **Persist immediately.** Deferred: in-memory proves the mechanism; a serialized cache is a drop-in
  implementation of the same port.

## Trade-offs

- (+) Reuse is now real and observable through `cache_hits` / `artifacts_reused` in the build log.
- (+) Correctness falls out of existing invariants: only `cacheable` (∴ deterministic, non-mutating)
  passes are cached, so sharing produced objects across runs is safe.
- (+) The cache is the validation lever for the DAG scheduler next: "did it execute only the
  uncached subgraph?" is a stronger test than "did it execute in order?"
- (−) `InMemoryPassCache` is process-local and unbounded — fine for a worker session; a persistent,
  evicting cache comes when the workload needs it.
- (−) Cached values are live object references; safe only because cacheable passes never mutate
  inputs — a property the invariants already guarantee, but one a persistent cache will enforce by
  serializing.

## Consequences

- Any long-lived caller gets incremental compiles for free; the API stays deterministic by choice.
- `cache_hit` / `artifacts_reused` are no longer placeholders — the metadata ADR-0014 collected now
  drives behavior.

## Future revisit

A persistent, size-bounded cache implementation of `PassCache`; the **DAG scheduler** consuming the
cache to execute only the uncached subgraph; and a **BuildManifest** — the immutable receipt for one
compilation (fingerprint, graph/pass versions, artifact hashes, repository state) — that replay and
auditing reference.
