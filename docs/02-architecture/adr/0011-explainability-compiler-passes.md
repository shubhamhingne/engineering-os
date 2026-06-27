# 0011 — Explainability as a compiler output, and the CompilerPass contract

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0007](0007-knowledge-synthesis.md), [ADR-0008](0008-decision-graph.md), [ADR-0009](0009-semantic-build-system.md), [ADR-0010](0010-build-planner-diff.md)

## Context

The system already turns a project idea into typed graphs (`KnowledgeGraph`,
`DecisionGraph`) and then into hashed artifacts (`ArtifactBundle`). What it could *not* do was
answer the question that makes the product more than a generator: **"why is this here, and what
did it produce?"** Knowing that "authentication" is a topic is cheap; being able to say *where it
was mentioned, which artifacts it shaped, which decisions it relates to, and how confident we are*
is the differentiator.

A convenience method — `graph.explain(entity)` — would have buried that capability inside the
knowledge model. Explainability is not a lookup; it is a **synthesis across every prior output**
(sources + knowledge + decisions + rendered bundle). It deserves to be a first-class artifact, the
same way `DecisionGraph` is.

Separately, each transformation in the pipeline (extract knowledge, extract decisions, build,
explain) had grown its own bespoke call shape. The "semantic compiler" was still a metaphor.

## Decision

**1. Explainability is another explicit compiler output.**

```
KnowledgeGraph + DecisionGraph + sources + ArtifactBundle → ExplanationExtractor → ExplanationGraph
```

An `Explanation` is a typed record per entity: `entity_id` (`topic:authentication`,
`tech:FastAPI`), `type`, `label`, `summary`, `evidence`, `sources` (where it was mentioned),
`appears_in` (artifacts it produced), `related_decisions`, and a `confidence` score derived from
how much evidence corroborates it. `ExplanationGraph` is versioned (`schema_version="v1"`) like
every other domain model.

**2. Every transformation is a `CompilerPass`.**

```python
class CompilerPass(Protocol):
    name: str
    consumes: list[str]      # required context keys (Dependencies)
    produces: list[str]      # context keys it adds (Output)
    deterministic: bool
    def run(self, context: dict) -> dict: ...
```

The pipeline becomes a literal **sequence of passes** over a shared context, run by a `PassRunner`
that validates each pass's declared inputs before invoking it:

```
ExtractKnowledgePass → ExtractDecisionPass → BuildPass → ExplainPass
```

`run_explain_pipeline(title, idea, sources)` composes them and returns the `ExplanationGraph`.
The endpoint `GET /projects/{id}/explanations` exposes it.

## Alternatives considered

- **`graph.explain(entity)` convenience method.** Rejected: hides a cross-output synthesis inside one
  model, makes it untestable in isolation, and couples explanation to the knowledge schema.
- **Keep bespoke per-stage call shapes.** Rejected: the compiler analogy stays metaphorical, passes
  can't be uniformly validated, cached, or reordered, and dependencies stay implicit.
- **Build authentication first** (the original Alpha-0.7 plan). Deferred: authentication is table
  stakes; a semantic explanation engine is part of the product's *identity*.

## Trade-offs

- (+) Explanation is a first-class, versioned, independently testable artifact — semantic tests assert
  provenance ("authentication appears in README.md", confidence > 0), not prose.
- (+) `CompilerPass` makes the pipeline introspectable: each pass declares what it consumes/produces,
  so the runner can validate dependencies and (later) cache deterministic passes by input hash.
- (+) New capabilities now fit a predictable slot — *add a pass*, not a special case.
- (−) One more abstraction layer; the passes share a dict context (typed context objects can come
  later if the key surface grows).
- (−) Confidence is a heuristic (evidence count), not a calibrated probability — honest, but coarse.

## Consequences

- `ExplanationGraph` joins `KnowledgeGraph` / `DecisionGraph` / `ArtifactBundle` as a typed output.
- The pipeline is now a list you can extend: `ComputeHashesPass`, `DiffArtifactsPass`, `PublishPass`
  slot in without changing the runner.
- `RepositoryState` (ADR-0010's future) has a natural home as another pass operating on the bundle.

## Future revisit

Promote the shared `context: dict` to a typed compiler context once the key surface stabilizes; add
`deterministic`-pass caching keyed by input hashes; record *why* an artifact regenerated (link the
diff back to the explanation that changed).
