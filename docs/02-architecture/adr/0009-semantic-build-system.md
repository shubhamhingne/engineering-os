# 0009 — Semantic build system: renderers, bundles, publishers

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0006](0006-export-pipeline.md), [ADR-0007](0007-knowledge-synthesis.md), [ADR-0008](0008-decision-graph.md)

## Context

Adding GitHub publishing the naive way would leak publishing logic into rendering. The system has
become, in effect, a **semantic build system**:

```
Project Knowledge → Semantic Compiler → Artifacts → Publishers
   (Vision/PRD)      (graphs+renderers)   (bundle)    (zip/github)
```

analogous to `source → compiler → binary`. README, ADRs, docs, and GitHub publishing are not
separate AI features — they're different outputs of one compilation process.

## Decision

Separate the pipeline into explicit layers:

1. **Graphs** — `KnowledgeGraph`, `DecisionGraph` (versioned semantic models).
2. **Renderers** — each consumes graphs/artifacts and produces explicit **`RenderedArtifact[]`**
   (`path`, `kind`, `content`, `provenance`). A **`RendererRegistry`** collects them into an
   **`ArtifactBundle`**. Renderers answer *what files should exist*.
3. **Publishers** — `ZipPublisher`, `GitHubPublisher` (and later GitLab, S3, filesystem) ship a
   bundle. Publishers answer *where the files go*. GitHub sits behind a `GitHubClient` port (real
   adapter in prod; a fake in tests).

Adding an output = implement one `Renderer`. Adding a destination = implement one `Publisher`.
Neither touches the other, and neither touches a central pipeline.

## Alternatives considered

- **GitHub as another renderer.** Rejected: conflates *what* with *where*; publishing logic would
  leak into rendering.
- **Publishing logic inside the export service.** Rejected: the export service should *orchestrate*
  render→publish, not contain GitHub specifics.

## Trade-offs

- (+) Clean separation that stays clean as outputs and destinations multiply.
- (+) ZIP and GitHub publish the **same bundle** — the synthesized README/ADR now ship in the ZIP too.
- (+) GitHub behind a client port → testable via a fake without touching the network.
- (−) More abstraction than a single export function — justified by the growth ahead.
- (−) The real GitHub push is gated on a token (Alpha-0.7 adds the user OAuth flow); proven here via
  the fake client.

## Consequences

- `RenderedArtifact` is explicit — provenance today; hashing, diffing, caching, and **incremental
  regeneration** become natural extensions (only re-render what changed).
- GitHub can later be treated as **synchronization** (commit SHA → graph metadata) rather than
  one-shot deployment.

## Future revisit

Add artifact metadata (`hash`, `generatedAt`) for caching/diffing; treat GitHub as sync (store the
commit SHA on the graph); add GitLab/Bitbucket/S3/filesystem publishers as needed.
