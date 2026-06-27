# 08 — Decision Log

A single index of significant decisions across the project, so the reasoning is discoverable in
one place. Architectural decisions are full ADRs; product and design decisions are captured in
their own docs and linked here.

## Architectural decisions (ADRs)

| ADR | Decision |
|---|---|
| [0001](../02-architecture/adr/0001-architecture.md) | Modular monolith with hexagonal core |
| [0002](../02-architecture/adr/0002-tech-stack.md) | Technology stack |
| [0003](../02-architecture/adr/0003-authentication.md) | Authentication & GitHub authorization |
| [0004](../02-architecture/adr/0004-artifact-abstraction.md) | Generalize VisionArtifact into a typed Artifact |
| [0005](../02-architecture/adr/0005-streaming-generation.md) | Streaming generation over SSE |
| [0006](../02-architecture/adr/0006-export-pipeline.md) | Export as an observable pipeline (ExportJob) |
| [0007](../02-architecture/adr/0007-knowledge-synthesis.md) | KnowledgeGraph synthesis + three-layer AI provenance |
| [0008](../02-architecture/adr/0008-decision-graph.md) | DecisionGraph + structured-model → renderer pattern |
| [0009](../02-architecture/adr/0009-semantic-build-system.md) | Semantic build system: renderers · bundle · publishers |
| [0010](../02-architecture/adr/0010-build-planner-diff.md) | Build planner, artifact hashing, and diff engine |
| [0011](../02-architecture/adr/0011-explainability-compiler-passes.md) | Explainability as a compiler output + the CompilerPass contract |
| [0012](../02-architecture/adr/0012-identity-federation-boundary.md) | Identity, GitHub federation, and the compiler boundary (CredentialProvider) |
| [0013](../02-architecture/adr/0013-typed-compiler-context.md) | Typed CompilerContext — symbol table, startup validator, CompilationReport |
| [0014](../02-architecture/adr/0014-compiler-fingerprint-and-dependency-graph.md) | Compiler fingerprint, pass versions, and the dependency graph |
| [0015](../02-architecture/adr/0015-repository-state-sync-pass.md) | RepositoryState and the RepositorySyncPass (GitHub as synchronization) |
| [0016](../02-architecture/adr/0016-pass-output-caching.md) | Pass-output caching (cache key binds pass version + input hash + fingerprint) |
| [0017](../02-architecture/adr/0017-dependency-driven-execution.md) | Dependency-driven execution and the ExecutionPlan (minimal subgraph) |
| [0018](../02-architecture/adr/0018-build-manifest.md) | BuildManifest — the immutable, content-addressed identity of a compilation |
| [0019](../02-architecture/adr/0019-compiler-hardening.md) | Compiler hardening — property-based invariant testing (Hypothesis) |

New ADRs use the
[template](https://github.com/shubhamhingne/.github/blob/main/docs/adr/0000-template.md).

## Product decisions

Captured in the case study: [design decisions](../04-case-study/03-design-decisions.md) ·
[trade-offs](../04-case-study/04-trade-offs.md) · [failure log](../04-case-study/05-failure-log.md).

## Beta readiness

Post-v1.0, the feature set is frozen and work shifts to beta hardening. Findings from the
Staff-Engineer readiness audit are tracked in the
[beta-readiness register](beta-readiness-register.md) (`BR-*`).

## Design decisions

Captured in the design system: [principles](../03-design-system/01-design-principles.md) and the
documented trade-off in each design doc.

## Concrete stack

The initial technology selection is documented in [tech-stack.md](tech-stack.md).

> Rule: a decision that is hard to reverse, crosses module boundaries, or chooses between credible
> alternatives gets recorded — here or as an ADR. Reversible, local choices do not.
