# 0017 — Dependency-driven execution and the ExecutionPlan

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0014](0014-compiler-fingerprint-and-dependency-graph.md), [ADR-0016](0016-pass-output-caching.md), [ADR-0013](0013-typed-compiler-context.md)

## Context

The compiler executed every pass in listed order and leaned on the cache to make repeats cheap. But
"run the whole list, skip what's cached" is not the same as "run only the work the change implies."
With descriptors (the dependency graph), fingerprints, input hashes, and a pass cache all in place,
the compiler had everything it needed to compute the **minimal subgraph** for a compile — and to do
so *predictively*, before executing.

This is correctness, not optimization. The right name is **dependency-driven execution**, not
"scheduling": execution can stay sequential and still run only the implied work.

## Decision

**`ExecutionPlan` — the predictive counterpart to `CompilationReport`.** Built from the dependency
graph and the cache *before* any pass runs, it states: the compiler `fingerprint`, the `required`
passes, the `reused` passes, the execution `order`, per-pass `reasons`, and the graph `edges`. The
report is historical; the plan is predictive. `Compiler.plan(seed)` produces it without executing
(it uses a non-counting `cache.peek`, so planning has no side effects).

**The pruning algorithm** (a single forward walk; the validated listed order is already topological):

```
build dependency graph → for each pass, in order:
    if any input is produced by a REQUIRED pass     → required (its input will change)
    elif its (pass, version, input_hash, fingerprint) is cached → reused
    else                                            → required
```

A pass is required exactly when something it transitively depends on will be recomputed, or its own
output isn't cached. Everything else is reused. `Compiler.run` executes only the required subgraph,
loading reused outputs from cache, and records the plan alongside the report.

**Conservative downstream propagation.** If an upstream pass is required, its dependents are required
too — even if re-execution would produce an identical output — because the plan cannot know the new
output before running. This is the standard, safe incremental-build rule.

**"Cached" and "up-to-date" are one category, deliberately.** I considered separate `skipped (cached)`
and `skipped (up-to-date)` lists. With a content-addressed pass cache they coincide: an output is
up-to-date *because* its `(pass, version, input_hash, fingerprint)` key is present. A separate
up-to-date category would be a dead field until a cache-less incremental store exists — which the
cache supersedes. So the plan has one `reused` list with a per-pass reason instead.

## Alternatives considered

- **Keep "run all, skip cached."** Rejected: it can't answer "what work does this change imply?" and
  makes the upcoming replay/audit story weaker. The plan is the artifact that answers it.
- **Parallel execution of independent passes.** Deliberately *not* built. Sequential topological
  execution stays deterministic, debuggable, replayable, and profileable. The graph already supports
  future parallelism; realizing it now buys little and costs determinism. Revisit after v1.0.
- **Two skip categories (cached vs up-to-date).** Rejected as a dead distinction under a content cache.

## Trade-offs

- (+) The compiler runs only the implied subgraph: change one input, only its dependents execute —
  proven by the minimal-subgraph tests, not asserted by ordering.
- (+) The plan is predictive and side-effect-free — a real dry-run capability (`Compiler.plan`).
- (+) The plan is the oracle for everything downstream: replay, audit, and a future scheduler all
  read it.
- (−) Conservative propagation may re-run a dependent that would have produced an identical output;
  safe and standard, and the cache still absorbs the cost on the next identical run.
- (−) `plan` then `run` walks the passes twice; the plan walk is cheap (hashing + peeks, no pass work).

## Consequences

- `CompilationResult` now carries the `ExecutionPlan`; `run` follows it. The architecture is
  `Pipeline → plan() → ExecutionPlan → run() → CompilationReport`.
- Execution remains sequential; only the *selection* of work changed. No pass implementation changed.

## Future revisit

A `BuildManifest` referencing the plan + report + hashes as an immutable receipt; parallel execution
of independent required passes (post-v1.0); and the plan as the contract a distributed executor would
consume.
