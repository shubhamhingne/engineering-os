# 19 — Compiler invariants

These are the properties that define the compiler. They are not features; they are the rules every
feature must preserve. The guiding question for any new work is no longer *"what should I build
next?"* but **"what invariant must this not violate?"** A change either preserves these or justifies
introducing a new one — explicitly, in an ADR.

| # | Invariant | Enforced by |
|---|---|---|
| 1 | **The compiler never knows the user.** It receives a `Project` and produces artifacts — no `User`, session, OAuth, or token reaches it. | Application boundary: `authenticate → authorize → compile(project) → publish(bundle, credential)` ([ADR-0012](adr/0012-identity-federation-boundary.md)) |
| 2 | **Renderers never publish.** They answer *what files exist*, producing an `ArtifactBundle`. | `RendererRegistry` / `ArtifactBundle` ([ADR-0009](adr/0009-semantic-build-system.md)) |
| 3 | **Publishers never render.** They answer *where files go*, and receive a credential — never OAuth. | `Publisher` + `CredentialProvider` port ([ADR-0009](adr/0009-semantic-build-system.md), [ADR-0012](adr/0012-identity-federation-boundary.md)) |
| 4 | **Passes declare their dependencies.** Every transformation exposes a `PassDescriptor` (typed consumes/produces). | `PassDescriptor` + startup validator ([ADR-0011](adr/0011-explainability-compiler-passes.md), [ADR-0013](adr/0013-typed-compiler-context.md)) |
| 5 | **The pipeline is provably well-formed.** No missing producer, no duplicate producer, no slot type mismatch — checked before any work runs. | `validate_pipeline`, called in `Compiler.__init__` ([ADR-0013](adr/0013-typed-compiler-context.md)) |
| 6 | **Graphs are versioned.** `KnowledgeGraph`, `DecisionGraph`, `ExplanationGraph`, `ArtifactBundle` all carry `schema_version`. | Typed domain models ([ADR-0007](adr/0007-knowledge-synthesis.md), [ADR-0008](adr/0008-decision-graph.md)) |
| 7 | **Artifacts are hashed.** Every `RenderedArtifact` carries a content hash; diffing and incremental build follow. | Artifact hashing + `DiffEngine` ([ADR-0010](adr/0010-build-planner-diff.md)) |
| 8 | **Explainability is explicit.** It is a first-class compiler output (`ExplanationGraph`), not a convenience method. | `ExplanationExtractor → ExplanationGraph` ([ADR-0011](adr/0011-explainability-compiler-passes.md)) |
| 9 | **Every compile is observable.** A run yields a `CompilationReport` — the build log of what ran, produced, and reused. | `CompilationReport` ([ADR-0013](adr/0013-typed-compiler-context.md)) |
| 10 | **Every run is fingerprinted.** The report pins not just the inputs but the compiler configuration that produced them, and each pass records why it ran. | `compute_fingerprint` + per-pass hashing ([ADR-0014](adr/0014-compiler-fingerprint-and-dependency-graph.md)) |
| 11 | **Every produced slot has exactly one producer.** Ownership of compiler state is unambiguous — no two passes write the same `ContextKey`. | `validate_pipeline` duplicate-producer check ([ADR-0013](adr/0013-typed-compiler-context.md), [ADR-0014](adr/0014-compiler-fingerprint-and-dependency-graph.md)) |

## The rule

A design that breaks one of these is rejected, exactly as it would be for the
[architecture principles](08-system-architecture.md#architecture-principles-non-negotiable). When a
new capability genuinely needs to change an invariant, that is a deliberate architectural decision:
it gets its own ADR, stating which invariant changes and why the trade is worth it.

This is what separates a project that accumulates features from one guided by a coherent design.
