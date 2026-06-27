# Architecture history

This is not a changelog. A changelog records *what* changed; this records *why the architecture
became what it is*. Each entry is a problem the system hit, the **missing concept** that resolved it,
and the insight that generalized. The pattern across all of them is one move: when a problem appeared,
the answer was never a utility class — it was asking *"what is the missing concept?"*, naming it as a
typed model, and letting the implementation fall out simpler.

For the resulting model see the [specification](docs/02-architecture/20-compiler-specification.md);
for the rules it must hold, the [invariants](docs/02-architecture/19-compiler-invariants.md); for the
dated decisions with their alternatives and trade-offs, the [ADRs](docs/02-architecture/adr/).

## The throughline

> **Every new capability became an explicit typed model before it became code.**

Knowledge → `KnowledgeGraph`. Decisions → `DecisionGraph`. Explanations → `ExplanationGraph`. Build
state → `ExecutionPlan`. Execution → `CompilationReport`. Identity → `BuildManifest`. Remote
observation → `RepositoryState`. Once the concept existed, the code got smaller.

A second throughline runs underneath it: **move correctness earlier.** Strings became typed graphs;
implicit relationships became declared dependencies; runtime failures became startup validation;
informal rules became invariants that require an ADR to change. Each release shrank the space of
invalid states *before* execution.

## Milestones and the insight each one bought

| Milestone | Missing concept | Architectural insight |
|---|---|---|
| **README synthesis** ([ADR-0007](docs/02-architecture/adr/0007-knowledge-synthesis.md)) | `KnowledgeGraph` | **Separate semantics from documents.** Build a typed model of the project; render text from it. The model is the product. |
| **ADR generation** ([ADR-0008](docs/02-architecture/adr/0008-decision-graph.md)) | `DecisionGraph` | Decisions are *derived* and structured, not authored prose — same structured-model → renderer pattern as the README. |
| **Renderer/Publisher split** ([ADR-0009](docs/02-architecture/adr/0009-semantic-build-system.md)) | `ArtifactBundle` + publishers | **Separate representation from transport.** *What files exist* (renderers) is independent of *where they go* (publishers). |
| **Incremental build** ([ADR-0010](docs/02-architecture/adr/0010-build-planner-diff.md)) | hashing + planner + diff | **Know what changed.** Content-address artifacts so generation can be conditional and publishing incremental. |
| **Explainability + passes** ([ADR-0011](docs/02-architecture/adr/0011-explainability-compiler-passes.md)) | `CompilerPass` + `ExplanationGraph` | **Capabilities become typed transformations.** The pipeline is a sequence of passes; explainability is an explicit output, not a method. |
| **Identity & federation** ([ADR-0012](docs/02-architecture/adr/0012-identity-federation-boundary.md)) | the application boundary | **The compiler never knows the user.** Identity wraps the compiler; a credential reaches publishers through a port, never OAuth. |
| **Typed `CompilerContext`** ([ADR-0013](docs/02-architecture/adr/0013-typed-compiler-context.md)) | the symbol table | **Move correctness to startup.** Typed slots + a validator make an ill-formed pipeline fail at construction, not mid-run. |
| **Fingerprint + dependency graph** ([ADR-0014](docs/02-architecture/adr/0014-compiler-fingerprint-and-dependency-graph.md)) | compiler self-knowledge | **The compiler can describe itself.** "Did the inputs change?" and "did the compiler change?" become separable questions. |
| **Repository synchronization** ([ADR-0015](docs/02-architecture/adr/0015-repository-state-sync-pass.md)) | `RepositoryState` | **Separate publication state from provider.** Model the state of publication; GitHub is one implementation, added as one pass. |
| **Pass-output caching** ([ADR-0016](docs/02-architecture/adr/0016-pass-output-caching.md)) | the cache key | **Activate metadata as reuse.** The fingerprint, version, and input hash the compiler already tracked become a reuse key. |
| **Dependency-driven execution** ([ADR-0017](docs/02-architecture/adr/0017-dependency-driven-execution.md)) | `ExecutionPlan` | **Separate planning from execution.** Run only the work the change implies — the minimal subgraph, predicted before executing. |
| **BuildManifest** ([ADR-0018](docs/02-architecture/adr/0018-build-manifest.md)) | semantic identity | **Separate semantic identity from execution identity.** *What exists* (manifest) is not *how it ran* (plan/report). |
| **Compiler hardening** ([ADR-0019](docs/02-architecture/adr/0019-compiler-hardening.md)) | properties over examples | **Prove the invariants, don't assert them.** With this many invariants, describe the space and let a generator attack it. |
| **Specification** ([doc 20](docs/02-architecture/20-compiler-specification.md)) | the authoritative model | **Make the model govern the code.** The spec is the contract; if spec and code disagree, the code is the bug. |

## What stayed constant

The clearest evidence that these were extensions rather than rewrites is the one number that didn't
move: across OAuth, repository synchronization, caching, and dependency-driven execution, the explain
pipeline's **compiler fingerprint never changed** — because none of those releases touched the
existing passes. OAuth layered *outside* the compiler; sync became *another pass*; dependency-driven
execution changed the *execution strategy*, not the semantics; caching *activated* metadata rather than
altering any pass contract. Architectural stability, made observable.

At v1.0 the fingerprint was moved deliberately, once, to mark the frozen model (`1.0`,
`50d50ff3b2b8`). From here it moves only when the [specification](docs/02-architecture/20-compiler-specification.md#governance)
does.
