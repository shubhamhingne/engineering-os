# 06 — Lessons Learned

A living document. Captured during the product-and-architecture phase, before implementation —
which is itself one of the lessons. These are reflections, not achievements.

## On scope

- **A narrow MVP is a design skill, not a limitation.** The hardest and most valuable decision so
  far was cutting twelve plausible features ([05](05-failure-log.md)) down to one loop. Saying
  "not yet" well is harder than saying "yes," and it's what makes a solo build shippable.
- **Scope discipline compounds.** Every feature deferred removed downstream architecture,
  testing, and documentation burden. Cutting the vector DB didn't save one decision — it saved a
  dozen.

## On process

- **Separating product from implementation clarified both.** Defining the product (Day 4) before
  the architecture (Day 5) before any code meant each phase had a clean input. When I was tempted
  to design schema during the PRD, stopping made both documents better.
- **Standards before code pays immediately.** Building the `.github` standards first meant
  Engineering OS inherits CI, issue forms, and a lifecycle for free. The first repo proved the
  standards; the standards will shape every repo after.
- **Writing the reasoning down changes the reasoning.** Several decisions got *better* the moment
  I had to justify them in an ADR or trade-off doc. Forcing the "why not" surfaced weak arguments
  I'd otherwise have shipped.

## On honesty

- **Admitting what's unvalidated is more credible than hiding it.** The personas are hypotheses,
  not interview data, and saying so ([02](02-discovery.md)) makes the rest of the analysis
  trustworthy. A portfolio that overclaims research reads as junior.
- **The riskiest assumption deserves a name.** "Lowering the cost of discipline will change
  behavior" might be wrong. Stating it as the central, unproven bet is more senior than asserting
  certainty.

## On engineering judgment

- **Opinion is a feature.** The instinct to make everything configurable is usually a failure to
  decide. Choosing strong defaults (lifecycle, standards) is the harder, better move.
- **Avoid premature sophistication.** Multi-agent, RAG, fine-tuned models — each is "modern" and
  each was wrong for the MVP. Reaching for sophistication before the simple version is proven is a
  common senior-engineer trap I had to actively resist.

## Release retrospective — v1.0-α1 (pass-output caching)

1. **What user problem did this solve?** Wasted work. A long-lived compiler now reuses any pass whose
   inputs, version, and compiler haven't changed — `cache_hits` and `artifacts_reused` go from honest
   zeros to observable reuse.
2. **What architectural decision made it possible?** The metadata was *already there*. Caching just
   bound it into a key — `hash(pass_id, pass_version, input_hash, compiler_fingerprint)` — and added a
   `PassCache` port injected at the boundary ([ADR-0016](../02-architecture/adr/0016-pass-output-caching.md)).
   Correctness fell out of the invariants: only `cacheable` (∴ deterministic, non-mutating) passes are
   cached, so `RepositorySyncPass` keeps reading live remote state.
3. **What trade-off did I consciously accept?** Cache is injected, not global — per-request API
   handlers stay cache-less and deterministic; a worker opts in. And `InMemoryPassCache` is
   process-local and unbounded — the mechanism, not yet the persistence.
4. **If I rebuilt this in a year, what would I change?** Nothing about the approach — this is the
   v1.0 thesis in miniature: each step *activates capability already present* rather than adding a new
   concept. The cache is also the lever that makes the DAG scheduler testable next ("did it run only
   the uncached subgraph?").

## Release retrospective — Alpha-0.9 (repository synchronization)

1. **What user problem did this solve?** "Is what I published current?" The system can now observe the
   remote and report `in_sync` / `ahead` / `unpublished`, with the exact set of pending artifacts —
   GitHub as *synchronization*, not fire-and-forget upload.
2. **What architectural decision made it possible?** Modelling `RepositoryState` as the remote
   analogue of `CompilationReport` — *state of publication*, transport-independent — and adding a
   single `RepositorySyncPass` that only *observes* (the planner still decides what to build, the
   publisher how to transmit) ([ADR-0015](../02-architecture/adr/0015-repository-state-sync-pass.md)).
   The credential rides in the reader as configuration, so it never enters the hashed symbol table.
3. **What trade-off did I consciously accept?** I deliberately constrained the release to *pure
   addition* — one `ContextKey`, one pass, one report section, zero edits to existing passes — even
   where a small edit would have been convenient. `last_sync` and `remote_fingerprint` ship as honest
   placeholders rather than half-built features.
4. **If I rebuilt this in a year, what would I change?** Nothing about the shape. The fact that this
   landed as addition — the explain pipeline's fingerprint is byte-for-byte identical before and after
   — is the result I was testing for: the architecture extends instead of entangling.

## Release retrospective — Alpha-0.8.y (compiler self-knowledge)

1. **What user problem did this solve?** Reproducibility and trust. The compiler can now answer not
   just "did the inputs change?" but "did the *compiler* change?" — and every pass can say *why* it
   ran. When identical inputs produce different outputs after an upgrade, that's now explainable.
2. **What architectural decision made it possible?** A `CompilerFingerprint` hashing the whole
   configuration (compiler version, every pass's `id+version+consumes+produces`, schema versions,
   renderer/publisher registries), `version` on each `PassDescriptor`, per-pass input/output hashes
   with an `invalidation_reason`, and the dependency graph built from descriptors as a *validation
   artifact* — cycle detection, reachability, visualization — with execution still sequential
   ([ADR-0014](../02-architecture/adr/0014-compiler-fingerprint-and-dependency-graph.md)).
3. **What trade-off did I consciously accept?** I built the DAG but did **not** schedule on it — it's
   diagnostics today, the scheduler's input tomorrow. And `cache_hit` stays inert and
   `invalidation_reason` reads "cold build" until reports are persisted — honest about what isn't
   there yet, rather than faking a cache.
4. **If I rebuilt this in a year, what would I change?** Nothing — this is the same trajectory every
   release has followed: move correctness earlier. Hashes → diff, strings → typed keys, runtime →
   startup, and now opaque runs → fingerprinted, self-explaining ones.

## Release retrospective — Alpha-0.8.x (the typed compiler)

1. **What user problem did this solve?** Indirectly but importantly: trust in the engine. The
   compiler can now prove its own pipeline is well-formed *before* running, and every compile emits a
   build log (`GET /compilation-report`) — which passes ran, what they produced, how long they took.
2. **What architectural decision made it possible?** Treating the context not as a typed bag but as
   the compiler's **symbol table**: typed `ContextKey` slots, a `PassDescriptor` per pass, a startup
   validator that proves "every consumed slot has a producer, types match, no duplicates," and a
   `CompilationReport` ([ADR-0013](../02-architecture/adr/0013-typed-compiler-context.md)). An
   ill-formed pipeline now fails at construction, not three passes deep.
3. **What trade-off did I consciously accept?** More machinery around a still-*sequential* pipeline,
   and report fields (`cache_hit`, `artifacts_reused`, `commit_sha`) that are present but inert until
   caching and RepositoryState land. I accepted both to keep the report shape stable and to make the
   eventual DAG scheduler a no-op for pass authors — the executor already reads only descriptors.
4. **If I rebuilt this in a year, what would I change?** Nothing structural — this is the home the
   project's invariants needed. I'd only have reached for it one release sooner, before the dict
   context had a chance to ossify.

## Release retrospective — Alpha-0.8 (identity, federation, and the boundary)

1. **What user problem did this solve?** Proving who you are and that you're allowed to publish.
   GitHub OAuth signs you in, your projects become yours (others get `403`), and publishing uses
   *your* token — no shared secret.
2. **What architectural decision made it possible?** Adding identity as application-layer services
   that **wrap** the compiler, never enter it ([ADR-0012](../02-architecture/adr/0012-identity-federation-boundary.md)).
   The request path is `authenticate → authorize(project) → compile(project) → publish(bundle, credential)`,
   and a `CredentialProvider` port hands the publisher a token without it ever learning OAuth exists —
   the same dependency inversion as renderers/publishers.
3. **What trade-off did I consciously accept?** GitHub-only login and a flat ownership model (no
   teams, roles, or local accounts) — because today this is a *publishing* platform, not a
   collaboration one. And server-side sessions over stateless JWTs: revocable and simple now, a
   caching concern only at far greater scale. The hard line I refused to cross: the compiler must not
   know who the user is, so it stays runnable in a CLI, CI, or a test with no session.
4. **If I rebuilt this in a year, what would I change?** Nothing about the boundary — that's the part
   I'd protect hardest. I'd reach sooner for the typed `CompilerContext` so the boundary is enforced
   by types at startup, not just by discipline.

## Release retrospective — Alpha-0.7 (explainability + compiler passes)

1. **What user problem did this solve?** Trust. The tool can now answer *"why is this here, and what
   did it produce?"* for any entity — `authentication` was mentioned in the Vision, shaped README.md
   and the ADR, relates to these decisions, confidence 0.7. A generator that can't explain itself is
   a black box; this one shows its work.
2. **What architectural decision made it possible?** Making explainability an explicit compiler
   output — `ExplanationExtractor → ExplanationGraph` — rather than a `graph.explain()` convenience
   method, and unifying every transformation under a `CompilerPass` contract (declared
   inputs/outputs, deterministic, run over a shared context)
   ([ADR-0011](../02-architecture/adr/0011-explainability-compiler-passes.md)). The pipeline is now a
   literal *sequence of passes*: `ExtractKnowledge → ExtractDecision → Build → Explain`.
3. **What trade-off did I consciously accept?** I built explainability *before* authentication —
   against my own earlier sequencing — because authentication is table stakes and a semantic
   explanation engine is part of the product's identity. And confidence is a heuristic (evidence
   count), not a calibrated probability: honest and useful now, coarse by design.
4. **If I rebuilt this in a year, what would I change?** Promote the shared `context: dict` to a typed
   compiler context, cache `deterministic` passes by input hash, and link the diff back to the
   explanation that changed — so the system records *why* an artifact regenerated, not just that it did.

## Release retrospective — Alpha-0.6.x (incremental build pipeline)

1. **What user problem did this solve?** Not re-doing work that didn't change — and being able to
   say precisely *what* changed since the last export/publish (the basis for fast, trustworthy sync).
2. **What architectural decision made it possible?** Adding the compiler's planning + change phases:
   artifact **hashing**, a **`BuildPlanner`** (conditional generation with reasons), and a
   **`DiffEngine`** ([ADR-0010](../02-architecture/adr/0010-build-planner-diff.md)). The pipeline is now
   `Knowledge → Planner → Renderers → Bundle → Diff → Publishers`.
3. **What trade-off did I consciously accept?** Rule-based planning (not cost/priority-aware) and a
   simple content hash — enough to unlock incremental builds now, with room to grow, rather than
   over-engineering a build graph before it's needed.
4. **If I rebuilt this in a year, what would I change?** Add `RepositoryState` (per-artifact published
   hashes + commit SHA) so the diff runs against the *remote*, and have publishers consume the diff to
   push only changed files — turning GitHub publish into true synchronization.

## Release retrospective — Alpha-0.6 (semantic build system + GitHub)

1. **What user problem did this solve?** Getting a synthesized project *out* of the tool — as a
   ZIP today and a real GitHub repo next — without the output format dictating the architecture.
2. **What architectural decision made it possible?** Separating **renderers** (what files exist →
   an explicit `ArtifactBundle`) from **publishers** (where they go: ZIP, GitHub) with a
   `RendererRegistry` ([ADR-0009](../02-architecture/adr/0009-semantic-build-system.md)). The system
   is now a *semantic build system*: knowledge → compiler → artifacts → publishers.
3. **What trade-off did I consciously accept?** More abstraction (bundle + registry + publisher
   ports) than a single export function, and the real GitHub push gated on a token until OAuth lands
   — proven now via a fake client. I traded immediate end-to-end push for a clean seam that won't
   leak publishing logic into rendering as destinations multiply.
4. **If I rebuilt this in a year, what would I change?** Add artifact `hash`/`generatedAt` for
   diffing + **incremental regeneration** (only re-render what changed), and treat GitHub as
   *synchronization* — store the commit SHA on the graph so the system knows exactly what shipped.

## Release retrospective — Alpha-0.5 (ADR generation)

1. **What user problem did this solve?** A project's key decisions should be *recorded* (ADRs)
   without the author hand-writing them — and recorded honestly, traceable to the artifacts.
2. **What architectural decision made it possible?** The **`DecisionGraph`** and the
   *structured-model → renderer* pattern ([ADR-0008](../02-architecture/adr/0008-decision-graph.md)):
   `KnowledgeGraph → DecisionExtractor → DecisionGraph → ADR Renderer`. Same shape as the README —
   the pattern is now the system's grammar.
3. **What trade-off did I consciously accept?** I **versioned and typed the graphs now** (`v1`)
   instead of shipping more features on an untyped dict — a deliberate refactor-before-feature that
   trades speed today for safe schema evolution later.
4. **If I rebuilt this in a year, what would I change?** Add an AI-assisted decision-extraction pass
   behind the same renderer, render a multi-ADR index (not just the primary decision), and add
   `graph.explain(entity)` for explainable provenance.

## Release retrospective — Alpha-0.4 (README synthesis)

Every release answers four questions.

1. **What user problem did this solve?** Every generated project needs a credible landing page —
   a README that reflects the project's *actual* intent — without the author writing it by hand.
2. **What architectural decision made it possible?** The **`KnowledgeGraph`** ([ADR-0007](../02-architecture/adr/0007-knowledge-synthesis.md)) —
   an internal semantic model extracted from the artifacts. The README is *synthesized from the
   graph*, so it reasons over the project instead of concatenating documents.
3. **What trade-off did I consciously accept?** Deterministic heuristic extraction over a single AI
   prompt. It's less linguistically nuanced, but it's **testable** ("if the Vision mentions auth,
   the README contains it") and **provenance-rich** — properties I valued more than prose polish at
   this stage.
4. **If I rebuilt this in a year, what would I change?** Extract the graph with a structured-output
   AI pass for richer features/architecture (keeping the deterministic fallback + provenance), and
   persist the KnowledgeGraph as a first-class artifact so every document shares one source of truth.

## On export as a pipeline (Day 13 — the architecture pays off again)

- **Export reused streaming with zero new mechanism.** Because generation streaming was built into
  the domain (ADR-0005), the export pipeline streamed its phases the same way — same SSE shape,
  same client pattern. The "one mental model" the user asked for fell out of the architecture, not
  extra work.
- **Modeling `ExportJob`, not `RepositoryGenerator`, kept the door open.** Naming it a *job* with a
  status and history means GitHub push and new output formats are future *phases/fields*, not a
  rewrite ([ADR-0006](../02-architecture/adr/0006-export-pipeline.md)). The name encodes the roadmap.
- **A real ZIP beats a stubbed one.** The pipeline produces an actual downloadable archive
  (README + LICENSE + docs), verified by tests that open the ZIP — so the feature is provably done,
  not demo-shaped.

## On making it feel alive (Day 12 — streaming)

- **The "magical" feeling is mostly honesty about progress.** Streaming the real stages
  (building context → calling the model → drafting → saved) and letting the content grow isn't a
  gimmick — it's surfacing what the system is *actually* doing. The port already supported it
  (`stream` is just another method), so the moat was real, not theater.
- **A deterministic fake stream made the experience testable.** The fake provider streams in
  fixed chunks, so the whole SSE pipeline (stages → tokens → done → persisted version) is proven
  by tests with no network — the same payoff as slice #1, now for streaming.
- **SSE-over-POST forced a small, honest design choice.** `EventSource` is GET-only, so the client
  uses `fetch` + `ReadableStream`. Naming that constraint in [ADR-0005](../02-architecture/adr/0005-streaming-generation.md)
  beats discovering it mid-implementation.

## On the workspace architecture (Day 11 — the signature screen)

- **Why one shell, many capabilities.** Instead of a page per artifact, the workspace is a single
  `WorkspaceShell` composing four zones, and every artifact (Vision, PRD, README, ADR) is the same
  type-agnostic components fed different data. The cost of the *next* artifact's UI is now ~zero —
  the mirror of the domain decision in [ADR-0004](../02-architecture/adr/0004-artifact-abstraction.md).
- **The EDR caught the real risk before code.** [EDR-001](../08-decisions/edr-001-workspace.md)
  forced the question "will this scale to 20 artifacts?" *before* implementation. The answer
  shaped the architecture (data-driven tree, type-agnostic editor, one I/O hook) — far cheaper than
  discovering it after building 4 bespoke pages.
- **Designing in code first removed guesswork.** The verified HTML prototype was the spec; the
  React implementation transcribed it. No "design while coding," no rework loop — the most
  expensive part of UI work was already settled.
- **Separating I/O from presentation made everything testable.** `useWorkspace` is the only place
  that touches the network; every other component is pure (props → UI). That's the seam where tests
  (and later React Query) slot in without touching a single visual component.

## On generalizing the domain (Day 10 — slice #2)

- **Why we generalized `VisionArtifact` → `Artifact`.** Slice #1 modelled *Vision*; the product
  is about *artifacts*. Rather than copy the Vision table/service/endpoint for PRD (and again for
  README, ADR), we refactored to a typed `Artifact` + immutable `ArtifactVersion` *before* adding
  PRD. The result: PRD shipped as a new enum value, a prompt template, and zero new endpoints or
  UI. Adding README and ADR later is now nearly free. ([ADR-0004](../02-architecture/adr/0004-artifact-abstraction.md))
- **Refactor-before-feature paid off immediately.** Doing the generalization first meant the PRD
  feature was *small* — the architecture absorbed it. Had we added PRD first and refactored later,
  we'd have paid twice and risked a migration with real data.
- **The week of design was the reason this was cheap.** The artifact-centric domain we wrote on
  Day 5 was the target; Day 10 just *realized* it. The refactor felt like filling in a shape that
  was already drawn — which is exactly what up-front design is supposed to buy.
- **Version history validated the immutability principle.** "Everything generated belongs in Git;
  no hidden state" became concrete: every generate and edit appends a version, nothing is
  overwritten, and history is visible. The principle stopped being a slogan and became a feature.

## On implementation (Day 9 — first vertical slice)

- **The architecture survived contact with code.** Building one workflow end-to-end (create →
  generate Vision → edit → save → reopen) against the documented hexagon worked without rework:
  the `AIProviderPort` + fake adapter made the generation logic testable with zero network, and
  the module/adapter split held. The design paid for itself on day one of coding.
- **A fake adapter is the highest-leverage test tool.** Putting the AI behind a port meant the
  whole workflow is deterministically testable (11 passing tests) without a provider or a key.
  This is the concrete payoff of "providers are replaceable" — it's a *testability* win, not just
  a vendor-flexibility one.
- **Environment ≠ target.** The documented stack targets Python 3.12, but the only local
  interpreter was 3.9. Rather than fake the result, I made the type hints version-agnostic so the
  tests actually run and prove the slice — honesty over a green screenshot I couldn't stand behind.
- **A vertical slice exposes the real seams.** Persistence, validation, error handling, and
  observability all showed up in one small workflow — exactly as intended. The slice is small but
  it touched every layer, which is the point.

## What I would do differently already

- I would have written this case-study narrative *in parallel* with the work from day one, not
  inserted it later — the reasoning is freshest at the moment of decision, and reconstructing it
  afterward loses fidelity. (This document now starts at decision-time going forward.)

> This file is updated as the project progresses. Implementation and release will add lessons
> about the gap between the design on paper and the system in production.
