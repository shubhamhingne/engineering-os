# 0014 — Compiler fingerprint, pass versions, and the dependency graph

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0013](0013-typed-compiler-context.md), [ADR-0010](0010-build-planner-diff.md), [ADR-0011](0011-explainability-compiler-passes.md)

## Context

ADR-0013 made the pipeline a typed, validated symbol table that emits a build log. Two questions it
still couldn't answer: *"did the **compiler** change?"* (we hash artifacts, but not the engine that
produced them — so identical inputs yielding different outputs after an upgrade was a mystery) and
*"**why** did this pass run?"* (the report had timings, not causes). And while the pipeline is
linear, its real shape is a DAG we weren't yet making explicit.

These are all the same move the project has made at every step: **pull correctness and explanation
earlier**, from runtime toward the declared structure.

## Decision

**Pass versions.** `PassDescriptor` gains `version: int`. Bump it when a pass's algorithm changes
even though no schema or renderer changes — the output legitimately differs, and that fact belongs
to the pass, not to a global compiler version.

**Compiler fingerprint.** `compute_fingerprint` hashes the compiler *configuration* — compiler
version, every pass's `(id, version, consumes, produces)`, the graph `schema_versions`, and the
renderer/publisher registries. Every `CompilationReport` carries the fingerprint. Now a run records
*which compiler* produced it: "did the inputs change?" and "did the compiler change?" are separable.

**Per-pass hashing + invalidation reason.** Each `PassResult` records an `input_hash`, an
`output_hash`, and an `invalidation_reason`. Given a previous report, a pass explains itself —
*cold build*, *inputs changed*, or *inputs unchanged*. This extends explainability from project
entities to the compiler itself, and is the exact signal pass-caching will consume.

**The dependency graph as a validation artifact.** `build_dependency_graph` derives the DAG from
descriptors (producer → consumer edges). It powers cycle detection (folded into `validate_pipeline`),
unreachable-pass detection, and a Mermaid visualization, exposed at `GET /compiler/pipeline`.
**Execution stays sequential** — the graph is for validation and diagnostics today; the v1.0 DAG
scheduler will consume the very same structure.

## Alternatives considered

- **Tie output changes to a single global compiler version.** Rejected: too coarse — every pass
  bump would churn one number and lose which pass actually changed. Per-pass `version` + a composite
  fingerprint is precise.
- **Implement topological execution now.** Deferred to v1.0: the graph delivers cycle detection,
  reachability, and visualization with zero runtime change; scheduled execution is a separate step.
- **Compare full outputs to detect "why a pass ran."** Rejected: hashing inputs is cheap, stable,
  and is the same key caching needs.

## Trade-offs

- (+) Reproducibility is explainable: a fingerprint pins inputs *and* engine.
- (+) Every pass can justify its execution — the build log gains causes, not just timings.
- (+) Cycle/unreachable detection and visualization now; scheduler-ready DAG for free.
- (−) `cache_hit`/`artifacts_reused` remain inert until pass-caching lands, and `invalidation_reason`
  needs a *previous* report to be more than "cold build" — honest, since reports aren't persisted yet.
- (−) Hashing graphs each run is extra work — negligible at these sizes, and it unlocks caching.

## Consequences

- `Compiler.run(seed, previous=None)` threads the prior report so invalidation reasons sharpen once
  reports are stored. `GET /compiler/pipeline` makes the engine self-describing.
- The fingerprint and `input_hash` are the keys RepositoryState (Alpha-0.9) and pass-caching (v1.0)
  will build on — both arrive as *additions*, not edits.

## Future revisit

Persist reports so `invalidation_reason` reaches slot-level granularity; flip `cache_hit` live with
pass-output caching keyed on `cacheable` + `input_hash`; and let the DAG scheduler derive execution
order from the same descriptors.
