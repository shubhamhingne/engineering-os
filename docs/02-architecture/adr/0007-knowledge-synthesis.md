# 0007 — KnowledgeGraph synthesis + three-layer AI provenance

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0004](0004-artifact-abstraction.md), [ADR-0005](0005-streaming-generation.md)

## Context

The README is the landing page of every generated project. Concatenating Vision + PRD produces a
mediocre, untrustworthy document. The README must **reason over** the project's intent, and — like
every AI capability — expose *why* it produced what it did.

## Decision

Introduce a **`KnowledgeGraph`**: an internal semantic model (problem, solution, features, tech
stack, topics, audience, roadmap, risks) **extracted from the project's artifacts**. The README is
**synthesized from the graph**, not concatenated; every section carries **provenance** (which
artifacts it derived from), and the result is **scored** for completeness with a list of missing
sections.

This establishes a standard for every AI capability — the **three layers**:

```
1. Prompt / Knowledge   (the inputs: artifacts → KnowledgeGraph)
2. Reasoning metadata    (provenance per section + quality score)
3. Artifact              (the README itself)
```

Not chain-of-thought — *provenance*. Users understand why the system produced what it did.

## Alternatives considered

- **Prompt concatenation** (Vision + PRD → "write a README"). Rejected: brittle, no provenance, not
  testable semantically, and quality varies run to run.
- **A graph database.** Rejected: the model is small and in-process; a DB is overkill.
- **A single AI prompt with no structured model.** Rejected for the core path: non-deterministic and
  opaque. The KnowledgeGraph makes extraction testable and provenance explicit; AI can *enhance*
  sections later without losing either property.

## Trade-offs

- (+) **Semantic, testable, provenance-rich** — "if the Vision mentions authentication, the README
  contains it" is an actual test, not a hope.
- (+) Every future artifact (ADR, architecture, test plans) can read from the same graph.
- (+) The quality score makes completeness measurable and (deliberately) addictive.
- (−) Deterministic heuristic extraction is **less linguistically nuanced** than a frontier model.
  Accepted: testability + provenance now; an AI extraction pass is an enhancement, not a redesign.

## Consequences

- The KnowledgeGraph is the shared semantic substrate; README is its first consumer.
- AI capabilities are expected to expose the three layers — provenance is a product feature (trust).
- Semantic tests guard meaning, not markdown.

## Future revisit

Extract the graph with a structured-output AI pass for richer features/architecture (keeping the
deterministic fallback + provenance), and persist the graph as a first-class artifact so multiple
documents share one source of truth.
