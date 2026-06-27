# 19 — Compiler invariants

These are the properties that define the compiler. They are not features; they are the rules every
feature must preserve. The guiding question for any new work is no longer *"what should I build
next?"* but **"what invariant must this not violate?"** A change either preserves these or justifies
introducing a new one — explicitly, in an ADR. They are grouped by concern; as they grow, categories
scale better than a numbered list. The ★ ones are demonstrated by property-based tests ([ADR-0019](adr/0019-compiler-hardening.md)).

### Compiler

- **The compiler never knows the user.** It receives a `Project` and produces artifacts — no `User`, session, OAuth, or token reaches it. *(Application boundary, [ADR-0012](adr/0012-identity-federation-boundary.md))*
- **Passes declare their dependencies.** Every transformation exposes a typed `PassDescriptor` (consumes/produces). *([ADR-0011](adr/0011-explainability-compiler-passes.md), [ADR-0013](adr/0013-typed-compiler-context.md))*
- ★ **The pipeline is provably well-formed before it runs.** No missing producer, no duplicate producer, no slot type mismatch, no cycle — checked in `Compiler.__init__`. *([ADR-0013](adr/0013-typed-compiler-context.md))*
- ★ **Every produced slot has exactly one producer.** Ownership of compiler state is unambiguous. *([ADR-0013](adr/0013-typed-compiler-context.md))*

### Artifacts & outputs

- **Renderers never publish; publishers never render.** Renderers answer *what files exist* (an `ArtifactBundle`); publishers answer *where they go*, receiving a credential, never OAuth. *([ADR-0009](adr/0009-semantic-build-system.md), [ADR-0012](adr/0012-identity-federation-boundary.md))*
- **Graphs are versioned.** `KnowledgeGraph`, `DecisionGraph`, `ExplanationGraph`, `ArtifactBundle` carry `schema_version`. *([ADR-0007](adr/0007-knowledge-synthesis.md), [ADR-0008](adr/0008-decision-graph.md))*
- **Artifacts are content-addressed.** Every `RenderedArtifact` carries a content hash; diffing and incremental build follow. *([ADR-0010](adr/0010-build-planner-diff.md))*
- **Explainability is an explicit output** (`ExplanationGraph`), not a convenience method. *([ADR-0011](adr/0011-explainability-compiler-passes.md))*

### Execution

- **Cacheable ⇒ deterministic.** Only deterministic, non-mutating passes may be cached; a pass that reads live state is neither. *([ADR-0011](adr/0011-explainability-compiler-passes.md), [ADR-0016](adr/0016-pass-output-caching.md))*
- ★ **Dependency-driven execution is topological and minimal.** A run executes exactly the forward closure of what changed — no more. *([ADR-0017](adr/0017-dependency-driven-execution.md))*
- **Execution plans are side-effect-free.** `Compiler.plan` predicts without mutating state (it peeks, never counts). *([ADR-0017](adr/0017-dependency-driven-execution.md))*
- **Every compile is observable.** A run yields a `CompilationReport` — the build log of what ran, produced, and reused. *([ADR-0013](adr/0013-typed-compiler-context.md))*

### Identity

- ★ **Every run is fingerprinted.** The report pins the inputs *and* the compiler configuration; each pass records why it ran. *([ADR-0014](adr/0014-compiler-fingerprint-and-dependency-graph.md))*
- **Every compilation has exactly one immutable BuildManifest** — its content-addressed identity and canonical reference for replay, audit, and provenance. *([ADR-0018](adr/0018-build-manifest.md))*
- ★ **Equivalent artifacts imply equivalent manifests.** `manifest_hash` is *semantic identity* (compiler fingerprint + artifact hashes + repository state); `plan_id` / `report_id` are *execution identity*. Same artifacts ⇒ same manifest, regardless of how they were executed. *([ADR-0018](adr/0018-build-manifest.md), [ADR-0019](adr/0019-compiler-hardening.md))*

## The rule

A design that breaks one of these is rejected, exactly as it would be for the
[architecture principles](08-system-architecture.md#architecture-principles-non-negotiable). When a
new capability genuinely needs to change an invariant, that is a deliberate architectural decision:
it gets its own ADR, stating which invariant changes and why the trade is worth it.

This is what separates a project that accumulates features from one guided by a coherent design.
