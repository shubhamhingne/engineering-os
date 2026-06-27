# 0018 — BuildManifest: the immutable identity of a compilation

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0014](0014-compiler-fingerprint-and-dependency-graph.md), [ADR-0016](0016-pass-output-caching.md), [ADR-0017](0017-dependency-driven-execution.md), [ADR-0015](0015-repository-state-sync-pass.md)

## Context

After α2 the compiler produces several immutable products — graphs, an `ExecutionPlan`, a
`CompilationReport`, artifact hashes — plus the mutable `RepositoryState` observation. What was
missing was a single object that says *"exactly what compilation are we talking about?"* Replay,
audit, provenance, and synchronization were all stitching reports together by inference. Every
prerequisite (fingerprints, hashes, plan, report) was finally in place to mint one.

## Decision

Introduce **`BuildManifest`** — the immutable receipt and *identity* of one compilation. It is
intentionally tiny and **references** the immutable products by id; it never duplicates a graph,
report, or explanation:

```
BuildManifest
  manifest_hash            # the compilation's semantic identity (content-addressed)
  compiler_fingerprint
  plan_id                  # → locate the ExecutionPlan
  report_id                # → locate the CompilationReport
  repository_state_id      # → locate the RepositoryState, if any
  artifact_hashes
  generated_at             # wall-clock metadata; NOT part of the identity
```

It is a frozen dataclass — immutable by construction.

**`manifest_hash` is the semantic identity** — a hash over `(compiler_fingerprint, artifact_hashes,
repository_state_id)`. Same hash ⇔ the same compiler produced the same artifacts against the same
remote state. Different hash ⇔ something material changed.

**Identity is content-addressed** (like a git commit): the manifest *is* its hash. No separate random
id — that would let two identical compilations have different identities, defeating the purpose.

## Why the hash excludes plan_id and report_id (a refinement of the original sketch)

The first sketch hashed the plan and report ids into `manifest_hash`. I deliberately changed that. A
cold build and a fully-cached rebuild of identical inputs run *differently* (the plan is all-required
vs all-reused; the report's `cache_hit`/durations differ) but produce *identical artifacts*. The
manifest's question is "what compilation is this?" — about the **result**, not the **execution**. So:

- `manifest_hash` hashes the result (fingerprint + artifacts + remote state) → stable across cold/warm.
- `plan_id` / `report_id` remain *in the manifest body* for replay navigation — they pin the exact
  execution, but they do not define semantic identity.

This is the same distinction ADR-0017 drew between the predictive plan and the historical report,
carried into identity: `manifest_hash` = *what*, the referenced ids = *how*.

## Alternatives considered

- **Random/UUID manifest id.** Rejected: breaks "identical compilation ⇒ identical identity."
- **Hash plan_id + report_id into the identity** (the original sketch). Rejected: makes the identity
  execution-specific, so cold and warm rebuilds of the same inputs would look like different
  compilations.
- **Embed the full plan/report/graphs.** Rejected: the manifest must be tiny and reference, not
  duplicate — otherwise it's just another report.

## Trade-offs

- (+) One canonical, immutable reference object for replay, audit, provenance, and sync.
- (+) Instant semantic comparison: equal `manifest_hash` ⇒ semantically identical compilation.
- (+) Stable across execution strategy (cold vs warm), which is the genuinely useful comparison.
- (−) Resolving `plan_id` / `report_id` to objects needs a store; today they're content ids without a
  persistence layer behind them (the store is the natural next step, with replay).
- (−) A deliberate deviation from the original field-for-field sketch — justified above, and easy to
  revisit if a future use wants execution-specific identity (it would hash the ids back in).

## Consequences

- Invariant 12: **every compilation has exactly one immutable BuildManifest.** It is the canonical
  reference for replay, auditing, provenance, and synchronization.
- The compiler's five immutable products (KnowledgeGraph, DecisionGraph, ExplanationGraph,
  CompilationReport, BuildManifest) and one mutable observation (RepositoryState) now have a clean
  split: everything but the repository is a completed fact.
- `GET /projects/{id}/build-manifest` surfaces the receipt.

## Future revisit

A persistence layer that stores manifests/plans/reports by id (turning `plan_id`/`report_id` into
resolvable references), then **compiler replay** — reconstruct *why* a compilation behaved as it did
from its manifest. After that, compiler hardening (property-based and adversarial tests) before v1.0.
