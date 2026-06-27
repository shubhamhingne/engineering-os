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
