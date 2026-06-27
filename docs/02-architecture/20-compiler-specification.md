# 20 — The Engineering OS Compiler: a specification

This document is not a description of the code. It is the **specification** of the compiler — the
contract any implementation must satisfy. The Python in `apps/api` is *an* implementation; this is
the *language*. Where the two ever disagree, this document is the intended truth and the code is the
bug.

It is written to be teachable. The test of success: a senior engineer who reads this should be able
to predict *where a new capability belongs* before reading a line of the implementation.

---

## Part I — Mental model

Engineering OS is a **semantic compiler for software projects**. It takes a project — a title, an
idea, and a set of source documents — and compiles it into a bundle of standards-compliant
engineering artifacts (README, ADRs, docs, scaffold), the way a compiler takes source and produces a
binary.

The word *compiler* is load-bearing. It explains the whole shape of the system, and it is chosen in
deliberate contrast to two things this is **not**:

- **Not a template engine.** A template engine substitutes values into fixed text. This system first
  builds a *typed semantic model* of the project (what topics, what technologies, what decisions) and
  then renders artifacts from that model. The model is the product; the text is a projection of it.
- **Not an LLM workflow.** An LLM workflow chains prompts and trusts the output. Here, extraction is
  *deterministic where possible*, every transformation has a *typed contract*, and AI — when it
  arrives — is one *implementation* of a contract, never the architecture itself.

Why compilation, specifically? Because compilation is the discipline that has spent fifty years
answering the exact questions this system has: *What did we know? What should we do? What actually
happened? What exists now? Did anything change?* A compiler answers those with phases, typed
intermediate representations, dependency graphs, caching, and reproducible builds. Adopting that
frame let the system grow by adding *phases to a pipeline* rather than *features to a monolith*.

The pipeline, end to end:

```
Project
   │  semantic extraction
   ▼
KnowledgeGraph ─┐
DecisionGraph ──┤
ExplanationGraph┘
   │  planning
   ▼
ExecutionPlan          (predictive: what work this compile implies)
   │  execution
   ▼
ArtifactBundle ─┐
CompilationReport┘     (historical: what actually ran)
   │  identity
   ▼
BuildManifest          (the immutable receipt of the result)
   │  synchronization
   ▼
RepositoryState        (the one window onto the outside world)
```

Everything above `RepositoryState` is a **completed fact**. `RepositoryState` is the **outside
world**. That split is the spine of the model.

---

## Part II — Semantic model

The compiler's intermediate representations are typed, versioned graphs. Each carries a
`schema_version`; a new shape is a new version, never an untyped dict.

- **`KnowledgeGraph`** — what the project *is*: its topics and technology stack, extracted from the
  sources. The answer to *"what do we know?"*
- **`DecisionGraph`** — what the project *should do*: the architectural decisions implied by the
  knowledge. The answer to *"what should we do?"*
- **`ExplanationGraph`** — why each entity *is here*: for every topic or technology, its evidence
  (where it was mentioned), the artifacts it shaped, the decisions it relates to, and a confidence.
  The answer to *"why does this exist?"* — explainability as a first-class output, not a method.

They form a chain: sources → `KnowledgeGraph` → `DecisionGraph`, and then `KnowledgeGraph` +
`DecisionGraph` + sources + the rendered bundle → `ExplanationGraph`. Each is produced by exactly one
pass and consumed by name downstream.

A conforming implementation **must** keep these as typed, versioned models, and **must** produce
explanations by synthesis across the other outputs — never as a lookup on a single graph.

---

## Part III — Compiler model

The compiler is a sequence of **passes** over a typed **context**, planned and executed.

- **`CompilerContext`** is the compiler's *symbol table*. It holds values addressed by typed
  **`ContextKey`** slots (`KNOWLEDGE`, `DECISIONS`, `BUNDLE`, `EXPLANATIONS`, `REPOSITORY_STATE`, …).
  Every write is type-checked. Passes never address state by raw string.
- **`PassDescriptor`** is a pass's contract, as data: `id`, `version`, `consumes` (typed keys),
  `produces` (typed keys), `deterministic`, `cacheable`. The descriptor — not the code — is the
  single source of truth the rest of the compiler reasons about.
- A **pass** reads its declared `consumes` from the context and returns its declared `produces`. It
  performs no I/O it did not declare, and reaches for no infrastructure — infrastructure is handed in.
- **Validation** happens before any work runs. A pipeline is well-formed iff every consumed slot has
  exactly one producer (or is seeded), types match, and the dependency graph is acyclic. An ill-formed
  pipeline must fail at construction, not mid-run.
- The **`ExecutionPlan`** is *predictive*: built from the dependency graph and the cache before
  execution, it states the `required` passes, the `reused` passes, and the topological `order`. A pass
  is required iff something it transitively depends on will recompute, or its own output is not cached.
  Computing a plan must have no side effects.
- The **`CompilationReport`** is *historical*: per pass, what ran, how long, whether it was a cache
  hit, its input/output hashes, and why it ran; plus the schema versions touched and the compiler
  fingerprint. It is the build log.

The architecture is therefore `Pipeline → plan() → ExecutionPlan → run() → CompilationReport`. A
conforming implementation **must** execute only the required subgraph, and **must** keep the plan
(prediction) and the report (history) as distinct objects.

---

## Part IV — Identity

The compiler distinguishes three identities, and conflating them is a defect.

- **Compiler fingerprint** — a hash of the *configuration*: compiler version, every pass's
  `(id, version, consumes, produces)`, the graph schema versions, and the renderer/publisher
  registries. It answers *"which compiler is this?"* It must change when, and only when, the compiler
  itself changes — including a single pass `version` bump.
- **Execution identity** — `plan_id` and `report_id`, content hashes of the plan and report. They
  answer *"which run was this?"* A cold build and a cached rebuild of the same inputs have *different*
  execution identities.
- **Semantic identity** — `manifest_hash`, a hash of `(compiler fingerprint, artifact hashes,
  repository-state id)`. It answers *"what exists because of this compilation?"* A cold build and a
  cached rebuild of the same inputs have the *same* semantic identity. **Equivalent artifacts imply
  equivalent manifests.**

The **`BuildManifest`** is the immutable, content-addressed receipt of a compilation. It is
intentionally tiny: it *references* the immutable products (`plan_id`, `report_id`,
`repository_state_id`) and records the artifact hashes — it never duplicates a graph or a report. Its
identity is its `manifest_hash` (semantic identity), like a git commit. Every compilation has exactly
one.

**`RepositoryState`** is the remote analogue of the report: the state of *publication* — published
commit, remote artifact hashes, sync status, pending artifacts — independent of transport. It is the
single mutable observation in the model. GitHub is one implementation; the state names nothing about
GitHub.

---

## Part V — Extension model

New capability enters through one of five typed slots. If a proposed feature does not fit one, that is
a signal to reconsider the feature — not to bend the model.

- **Add a graph** — define a typed, versioned model and the pass that produces it. It becomes a new
  `ContextKey`. (You are extending *what we know*.)
- **Add a pass** — implement the `CompilerPass` contract: declare a `PassDescriptor`, read declared
  inputs, return declared outputs. Register it in a pipeline. The planner, cache, fingerprint, and
  report absorb it with no changes. (You are extending *what the compiler does*.)
- **Add a renderer** — implement the renderer contract to emit files into the `ArtifactBundle`.
  Renderers answer *what files exist*. (You are extending *the artifact set*.)
- **Add a publisher** — implement the publisher contract to ship a bundle to a destination, receiving
  a credential. Publishers answer *where files go*. (You are extending *publication targets*.)
- **Add a repository adapter** — implement the read-only `RepositoryReader` to observe a remote.
  (You are extending *which remotes we understand*.)

Each is an *addition*, not an *edit*. The proof obligation for any extension is that the existing
compiler fingerprint for the existing pipeline is unchanged.

---

## Part VI — Invariants

The compiler's invariants are specified and categorized in
[19 — Compiler invariants](19-compiler-invariants.md): **Compiler**, **Artifacts**, **Execution**,
**Identity**. They are normative. A change either preserves every invariant or amends one explicitly
in an ADR, stating which invariant changes and why. A conforming implementation must hold all of them;
the property-based suite ([ADR-0019](adr/0019-compiler-hardening.md)) demonstrates the load-bearing
ones over generated pipelines.

---

## Part VII — Design philosophy

These are the reasons the implementation has the shape it does. They are more durable than any class.

- **Move correctness earlier.** The trajectory of every release: strings → typed graphs; implicit
  relationships → declared dependencies; runtime failures → startup validation; documented rules →
  invariants requiring an ADR. Reduce the space of invalid states *before* execution.
- **Prefer composition over modification.** New capability composes into the pipeline; it does not
  ripple through it. The test is the fingerprint: extension leaves the existing one unchanged.
- **Infrastructure is injected.** The AI provider, OAuth provider, credential provider, repository
  reader, and pass cache are all handed in at the boundary. Nothing in the compiler reaches out to
  obtain infrastructure.
- **Semantic identity over execution identity.** What was produced matters more than how it was
  produced. The manifest identifies the result; the plan and report identify the run.
- **Every capability has a typed contract.** Passes, graphs, renderers, publishers, readers — each is
  a contract, so an implementation can be swapped (including for an AI one) without the architecture
  noticing.
- **The compiler is pure with respect to the world.** It receives a `Project` and produces facts. It
  never knows the user; the one window onto the outside world is `RepositoryState`, and even that is
  observed through an injected reader.

---

## Part VIII — Why we did *not* build X

The negative decisions define the architecture as sharply as the positive ones.

- **Why the compiler never knows the user.** If a `User`, session, or token entered the compiler, it
  could no longer run in a CLI, a CI job, a batch run, or a test without a logged-in user. Identity
  *wraps* the compiler; it does not enter it.
- **Why renderers never publish (and publishers never render).** Collapsing *what files exist* and
  *where they go* would couple the artifact set to its destinations. Kept apart, a new destination is a
  new publisher and a new artifact is a new renderer — neither touches the other.
- **Why `RepositoryState` is not a GitHub object.** Modeling *publication state* rather than a GitHub
  response keeps the transport swappable and the compiler ignorant of GitHub. State is about the world,
  not about an API.
- **Why manifests identify results, not executions.** A cold build and a cached rebuild of the same
  inputs are the same *compilation* even though they *ran* differently. Hashing the execution into the
  identity would make the receipt represent the wrong thing.
- **Why dependency execution stays sequential.** Topological sequential execution is deterministic,
  debuggable, replayable, and profileable. The dependency graph already permits parallelism; realizing
  it now would trade those properties for throughput the workload does not yet need.
- **Why AI is an implementation, not a primitive.** Making AI an architectural concept would let an
  opaque, non-deterministic stage define the system. Instead, AI is one implementation of a
  `CompilerPass` — declared `deterministic = false`, `cacheable = false` until proven otherwise — so
  the deterministic, typed, testable architecture survives its arrival.

---

## How to read the rest of the docs

- The **invariants** ([19](19-compiler-invariants.md)) are the normative rules.
- The **ADRs** ([decision log](../08-decisions/README.md)) are the dated decisions, each with the
  alternatives considered and trade-offs accepted — the *why* behind every part of this spec.
- The **case study** ([04](../04-case-study/)) is the narrative of how the model was discovered, one
  release at a time.

If this document and the code disagree, fix the code.
