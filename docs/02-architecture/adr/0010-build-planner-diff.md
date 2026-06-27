# 0010 — Build planner, artifact hashing, and diff engine

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0009](0009-semantic-build-system.md)

## Context

Generation was *unconditional*: every renderer ran on every export. As renderers multiply
(README, ADR, docs, OpenAPI, diagrams, pitch deck), that wastes work and makes incremental
publishing impossible — you can't push "only what changed" if you don't know what changed.

## Decision

Add the compiler's **planning** and **change-detection** phases:

```
KnowledgeGraph → BuildPlanner → BuildPlan → RendererRegistry → ArtifactBundle → DiffEngine → Publishers
```

1. **Hashing** — every `RenderedArtifact` carries a content `hash` (and an optional `generated_at`).
2. **BuildPlanner** — given the graph + available inputs, produces a `BuildPlan`: which renderers to
   run and *why* (e.g. `openapi → skip (no API spec)`, `diagrams → skip (missing architecture)`).
   Generation is now conditional, not unconditional.
3. **DiffEngine** — compares a previous bundle (path → content) against a new bundle by hash →
   `added / changed / unchanged / removed`. Endpoints expose the plan and the diff.

## Alternatives considered

- **Render everything, every time.** Simple. Rejected: wasteful and blocks incremental publish/sync.
- **Per-renderer ad-hoc conditionals.** Rejected: scatters planning logic across renderers instead of
  centralizing the decision in a planner.

## Trade-offs

- (+) Incremental builds (skip unchanged); the basis for incremental *publish* (push only changes).
- (+) The plan is explainable — it states what it will build and why.
- (+) Hashes are cheap and unlock diffing, caching, and sync.
- (−) More pipeline stages; the planner's heuristics are simple today (rules, not cost-based).

## Consequences

- After an export, re-diffing shows all-`unchanged` until an artifact actually changes — the system
  knows precisely what would need re-publishing.
- This is the foundation for **RepositoryState** (store last-published hashes → diff against the
  remote) and for treating GitHub as synchronization rather than re-upload.

## Future revisit

Add `RepositoryState` (per-artifact published hashes + commit SHA), have publishers consume the diff
to push only changed files, and grow the planner from rules toward cost/priority-aware planning.
